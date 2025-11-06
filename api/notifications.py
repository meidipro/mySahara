"""
Notification Service - Handles FCM push notifications for medications and vaccines
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime, timedelta
import os
from typing import List, Dict, Optional
import json
from loguru import logger

# Import Firebase Admin if available
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning("Firebase Admin SDK not available. Install with: pip install firebase-admin")

from services.supabase_client import get_supabase_client

router = APIRouter()

# Pydantic models for request validation
class SendNotificationRequest(BaseModel):
    token: str
    title: str
    body: str
    data: Optional[Dict[str, str]] = {}

class SendBulkNotificationRequest(BaseModel):
    tokens: List[str]
    title: str
    body: str
    data: Optional[Dict[str, str]] = {}

class MedicationReminderRequest(BaseModel):
    user_id: str
    medication_id: str
    schedule_id: Optional[str] = None
    owner_name: Optional[str] = "You"
    relationship: Optional[str] = None

class VaccineReminderRequest(BaseModel):
    user_id: str
    vaccine_id: str
    owner_name: Optional[str] = "You"
    relationship: Optional[str] = None
    days_until_due: Optional[int] = 0

class TestNotificationRequest(BaseModel):
    token: str

# Initialize Firebase Admin SDK
if FIREBASE_AVAILABLE and not firebase_admin._apps:
    try:
        # Method 1: Try loading from file path (local development)
        cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized from file")
        else:
            # Method 2: Try loading from JSON string (Render deployment)
            cred_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
            if cred_json:
                import json
                cred_dict = json.loads(cred_json)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized from JSON string")
            else:
                logger.warning("Firebase service account not configured. Set FIREBASE_SERVICE_ACCOUNT_PATH or FIREBASE_SERVICE_ACCOUNT_JSON")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")


@router.post("/send")
async def send_notification(request_data: SendNotificationRequest):
    """
    Send a push notification to a specific device
    """
    if not FIREBASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Firebase Admin SDK not available")

    try:
        # Create message
        message = messaging.Message(
            notification=messaging.Notification(
                title=request_data.title,
                body=request_data.body,
            ),
            data=request_data.data,
            token=request_data.token,
        )

        # Send message
        response = messaging.send(message)
        logger.info(f"Notification sent successfully: {response}")

        return {"success": True, "message_id": response}

    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-bulk")
async def send_bulk_notifications(request_data: SendBulkNotificationRequest):
    """
    Send notifications to multiple devices
    """
    if not FIREBASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Firebase Admin SDK not available")

    try:
        # Create message
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=request_data.title,
                body=request_data.body,
            ),
            data=request_data.data,
            tokens=request_data.tokens,
        )

        # Send message
        response = messaging.send_multicast(message)
        logger.info(f"Bulk notifications sent: {response.success_count} succeeded, {response.failure_count} failed")

        return {
            "success": True,
            "success_count": response.success_count,
            "failure_count": response.failure_count,
        }

    except Exception as e:
        logger.error(f"Error sending bulk notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/family-daily-summary/{user_id}")
async def send_family_daily_summary(user_id: str):
    """
    Send daily summary of family reminders to user

    Aggregates all medication and vaccine reminders for user and family members
    and sends a single comprehensive notification
    """
    if not FIREBASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Firebase Admin SDK not available")

    try:
        supabase = get_supabase_client()

        # Get user's FCM token
        user_response = supabase.table('users').select('fcm_token').eq('id', user_id).execute()

        if not user_response.data or not user_response.data[0].get('fcm_token'):
            raise HTTPException(status_code=404, detail="User not found or no FCM token")

        fcm_token = user_response.data[0]['fcm_token']

        # Get today's reminders
        today = datetime.now().date()
        tomorrow = (datetime.now() + timedelta(days=1)).date()

        reminders = []

        # Get user's medications
        user_meds_response = supabase.table('medications').select('*').eq('user_id', user_id).execute()

        for med in user_meds_response.data:
            # Get schedules for this medication
            schedules_response = supabase.table('medication_schedules').select('*').eq('medication_id', med['id']).execute()

            for schedule in schedules_response.data:
                reminders.append({
                    'type': 'medication',
                    'owner': 'You',
                    'name': med['name'],
                    'dosage': f"{med['dosage_amount']} {med['dosage_unit']}",
                    'time': schedule.get('time', '09:00'),
                })

        # Get family members
        family_response = supabase.table('family_members').select('*').eq('user_id', user_id).execute()

        for member in family_response.data:
            member_name = member['full_name']
            relationship = member.get('relationship', '')
            owner_display = f"{relationship} ({member_name})" if relationship else member_name

            # Get medications for family member
            member_meds_response = supabase.table('medications').select('*').eq('user_id', user_id).eq('family_member_id', member['id']).execute()

            for med in member_meds_response.data:
                schedules_response = supabase.table('medication_schedules').select('*').eq('medication_id', med['id']).execute()

                for schedule in schedules_response.data:
                    reminders.append({
                        'type': 'medication',
                        'owner': owner_display,
                        'name': med['name'],
                        'dosage': f"{med['dosage_amount']} {med['dosage_unit']}",
                        'time': schedule.get('time', '09:00'),
                    })

            # Get vaccines for family member
            member_vaccines_response = supabase.table('vaccines').select('*').eq('user_id', user_id).eq('family_member_id', member['id']).execute()

            for vaccine in member_vaccines_response.data:
                if vaccine.get('next_due_date'):
                    due_date = datetime.fromisoformat(vaccine['next_due_date'].replace('Z', '+00:00')).date()

                    if today <= due_date <= tomorrow:
                        reminders.append({
                            'type': 'vaccine',
                            'owner': owner_display,
                            'name': vaccine['vaccine_name'],
                            'dosage': f"Dose {vaccine['dose_number']}" + (f"/{vaccine['total_doses']}" if vaccine.get('total_doses') else ''),
                            'due_date': vaccine['next_due_date'],
                        })

        # Build notification message
        if not reminders:
            return {"message": "No reminders for today"}

        # Group by owner
        by_owner = {}
        for reminder in reminders:
            owner = reminder['owner']
            if owner not in by_owner:
                by_owner[owner] = []
            by_owner[owner].append(reminder)

        # Build message lines
        lines = []
        for owner, owner_reminders in by_owner.items():
            for reminder in owner_reminders:
                if reminder['type'] == 'medication':
                    lines.append(f"• {owner} - {reminder['name']} {reminder['dosage']} at {reminder['time']}")
                else:
                    lines.append(f"• {owner} - {reminder['name']} vaccine {reminder['dosage']}")

        title = f"{len(by_owner)} family member{'s' if len(by_owner) != 1 else ''} need{'s' if len(by_owner) == 1 else ''} attention today"
        body = '\n'.join(lines[:5])  # Limit to 5 lines for notification

        if len(lines) > 5:
            body += f"\n+ {len(lines) - 5} more reminders..."

        # Send notification
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data={
                'type': 'family_daily_summary',
                'reminder_count': str(len(reminders)),
            },
            token=fcm_token,
        )

        response = messaging.send(message)
        logger.info(f"Family daily summary sent to {user_id}: {response}")

        return {
            "success": True,
            "message_id": response,
            "reminder_count": len(reminders),
            "owners_count": len(by_owner),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending family daily summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/medication-reminder")
async def send_medication_reminder(request_data: MedicationReminderRequest):
    """
    Send medication reminder notification
    """
    if not FIREBASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Firebase Admin SDK not available")

    try:
        supabase = get_supabase_client()

        # Get user's FCM token
        user_response = supabase.table('users').select('fcm_token').eq('id', request_data.user_id).execute()

        if not user_response.data or not user_response.data[0].get('fcm_token'):
            raise HTTPException(status_code=404, detail="User not found or no FCM token")

        fcm_token = user_response.data[0]['fcm_token']

        # Get medication details
        med_response = supabase.table('medications').select('*').eq('id', request_data.medication_id).execute()

        if not med_response.data:
            raise HTTPException(status_code=404, detail="Medication not found")

        medication = med_response.data[0]

        # Build notification message
        owner_display = f"{request_data.relationship} ({request_data.owner_name})" if request_data.relationship else request_data.owner_name
        title = f"💊 Time to take {medication['name']}"
        body = f"{owner_display} - {medication['dosage_amount']} {medication['dosage_unit']}"

        if medication.get('instructions'):
            body += f"\n{medication['instructions']}"

        # Send notification
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data={
                'type': 'medication',
                'medication_id': request_data.medication_id,
                'schedule_id': request_data.schedule_id or '',
                'owner_name': request_data.owner_name,
            },
            token=fcm_token,
        )

        response = messaging.send(message)
        logger.info(f"Medication reminder sent to {request_data.user_id}: {response}")

        return {"success": True, "message_id": response}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending medication reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vaccine-reminder")
async def send_vaccine_reminder(request_data: VaccineReminderRequest):
    """
    Send vaccine reminder notification
    """
    if not FIREBASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Firebase Admin SDK not available")

    try:
        supabase = get_supabase_client()

        # Get user's FCM token
        user_response = supabase.table('users').select('fcm_token').eq('id', request_data.user_id).execute()

        if not user_response.data or not user_response.data[0].get('fcm_token'):
            raise HTTPException(status_code=404, detail="User not found or no FCM token")

        fcm_token = user_response.data[0]['fcm_token']

        # Get vaccine details
        vaccine_response = supabase.table('vaccines').select('*').eq('id', request_data.vaccine_id).execute()

        if not vaccine_response.data:
            raise HTTPException(status_code=404, detail="Vaccine not found")

        vaccine = vaccine_response.data[0]

        # Build notification message
        owner_display = f"{request_data.relationship} ({request_data.owner_name})" if request_data.relationship else request_data.owner_name

        # Contextual time message
        days_until_due = request_data.days_until_due
        if days_until_due < 0:
            time_text = f"overdue by {abs(days_until_due)} days"
        elif days_until_due == 0:
            time_text = "due today"
        elif days_until_due == 1:
            time_text = "due tomorrow"
        else:
            time_text = f"due in {days_until_due} days"

        title = f"💉 {vaccine['vaccine_name']} vaccine {time_text}"
        body = f"{owner_display} - Dose {vaccine['dose_number']}"

        if vaccine.get('total_doses'):
            body += f"/{vaccine['total_doses']}"

        if vaccine.get('location'):
            body += f"\nLocation: {vaccine['location']}"

        # Send notification
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data={
                'type': 'vaccine',
                'vaccine_id': request_data.vaccine_id,
                'owner_name': request_data.owner_name,
            },
            token=fcm_token,
        )

        response = messaging.send(message)
        logger.info(f"Vaccine reminder sent to {request_data.user_id}: {response}")

        return {"success": True, "message_id": response}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending vaccine reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_notification(request_data: TestNotificationRequest):
    """
    Test notification endpoint - sends a test notification to verify FCM setup
    """
    if not FIREBASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Firebase Admin SDK not available")

    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title="mySahara Test Notification",
                body="Your notification system is working correctly!",
            ),
            data={'type': 'test'},
            token=request_data.token,
        )

        response = messaging.send(message)
        logger.info(f"Test notification sent: {response}")

        return {"success": True, "message_id": response}

    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))
