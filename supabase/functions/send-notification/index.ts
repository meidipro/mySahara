// Firebase Cloud Messaging V1 API - Send Notification
// Supabase Edge Function for sending push notifications using FCM V1 API

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// CORS headers
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface NotificationRequest {
  userId?: string
  fcmToken?: string
  title: string
  body: string
  data?: Record<string, string>
  imageUrl?: string
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { userId, fcmToken, title, body, data, imageUrl }: NotificationRequest = await req.json()

    // Get FCM token from database if userId provided
    let targetToken = fcmToken
    if (userId && !fcmToken) {
      const supabaseClient = createClient(
        Deno.env.get('SUPABASE_URL') ?? '',
        Deno.env.get('SUPABASE_ANON_KEY') ?? '',
        { global: { headers: { Authorization: req.headers.get('Authorization')! } } }
      )

      const { data: user, error } = await supabaseClient
        .from('users')
        .select('fcm_token')
        .eq('id', userId)
        .single()

      if (error || !user?.fcm_token) {
        return new Response(
          JSON.stringify({ error: 'User not found or FCM token not available' }),
          { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        )
      }

      targetToken = user.fcm_token
    }

    if (!targetToken) {
      return new Response(
        JSON.stringify({ error: 'FCM token is required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Get Firebase credentials from environment
    const serviceAccount = JSON.parse(Deno.env.get('FIREBASE_SERVICE_ACCOUNT') ?? '{}')

    if (!serviceAccount.project_id) {
      return new Response(
        JSON.stringify({ error: 'Firebase service account not configured' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Get OAuth2 access token
    const accessToken = await getAccessToken(serviceAccount)

    // Send notification using FCM V1 API
    const fcmResponse = await fetch(
      `https://fcm.googleapis.com/v1/projects/${serviceAccount.project_id}/messages:send`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          message: {
            token: targetToken,
            notification: {
              title,
              body,
              ...(imageUrl && { image: imageUrl }),
            },
            data: data || {},
            android: {
              priority: 'high',
              notification: {
                sound: 'default',
                priority: 'high',
              },
            },
            apns: {
              payload: {
                aps: {
                  sound: 'default',
                  badge: 1,
                },
              },
            },
          },
        }),
      }
    )

    const fcmResult = await fcmResponse.json()

    if (!fcmResponse.ok) {
      console.error('FCM Error:', fcmResult)
      return new Response(
        JSON.stringify({ error: 'Failed to send notification', details: fcmResult }),
        { status: fcmResponse.status, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    return new Response(
      JSON.stringify({ success: true, result: fcmResult }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('Error:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})

// Get OAuth2 access token for FCM V1 API
async function getAccessToken(serviceAccount: any): Promise<string> {
  const jwtHeader = {
    alg: 'RS256',
    typ: 'JWT',
  }

  const now = Math.floor(Date.now() / 1000)
  const jwtClaimSet = {
    iss: serviceAccount.client_email,
    scope: 'https://www.googleapis.com/auth/firebase.messaging',
    aud: 'https://oauth2.googleapis.com/token',
    exp: now + 3600,
    iat: now,
  }

  // Create JWT
  const encodedHeader = base64UrlEncode(JSON.stringify(jwtHeader))
  const encodedClaimSet = base64UrlEncode(JSON.stringify(jwtClaimSet))
  const signatureInput = `${encodedHeader}.${encodedClaimSet}`

  // Sign JWT with private key
  const privateKey = await importPrivateKey(serviceAccount.private_key)
  const signature = await crypto.subtle.sign(
    {
      name: 'RSASSA-PKCS1-v1_5',
      hash: { name: 'SHA-256' },
    },
    privateKey,
    new TextEncoder().encode(signatureInput)
  )

  const jwt = `${signatureInput}.${base64UrlEncode(signature)}`

  // Exchange JWT for access token
  const response = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${jwt}`,
  })

  const data = await response.json()
  return data.access_token
}

// Import RSA private key
async function importPrivateKey(pem: string): Promise<CryptoKey> {
  const pemContents = pem
    .replace(/-----BEGIN PRIVATE KEY-----/, '')
    .replace(/-----END PRIVATE KEY-----/, '')
    .replace(/\n/g, '')

  const binaryDer = Uint8Array.from(atob(pemContents), c => c.charCodeAt(0))

  return await crypto.subtle.importKey(
    'pkcs8',
    binaryDer,
    {
      name: 'RSASSA-PKCS1-v1_5',
      hash: 'SHA-256',
    },
    false,
    ['sign']
  )
}

// Base64 URL encoding
function base64UrlEncode(data: string | ArrayBuffer): string {
  let base64: string
  if (typeof data === 'string') {
    base64 = btoa(data)
  } else {
    base64 = btoa(String.fromCharCode(...new Uint8Array(data)))
  }
  return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '')
}
