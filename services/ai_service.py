"""
AI Service for chat and health analysis.
Uses Groq API (primary) and Gemini API (fallback).
"""

import os
import time
from typing import Dict, Any, Optional, List
from groq import Groq
import google.generativeai as genai
from loguru import logger


class AIService:
    """
    Service for AI chat and health analysis using Groq and Gemini APIs.
    """

    def __init__(self):
        """
        Initialize AI service with API credentials.
        """
        # Initialize Groq client
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if self.groq_api_key:
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {str(e)}")
                self.groq_client = None
        else:
            logger.warning("GROQ_API_KEY not found")
            self.groq_client = None

        # Initialize Gemini client
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Gemini client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {str(e)}")
                self.gemini_model = None
        else:
            logger.warning("GEMINI_API_KEY not found")
            self.gemini_model = None

        # System prompts
        self.medical_system_prompt_en = """You are a helpful medical health assistant for mySahara Health App.
Your role is to provide accurate, empathetic, and culturally sensitive health information to users in Bangladesh and globally.

Key guidelines:
- Provide evidence-based health information
- Be empathetic and understanding
- Always include a disclaimer that you're not replacing professional medical advice
- Encourage users to consult healthcare professionals for serious concerns
- Be culturally sensitive to Bangladeshi context
- Keep responses clear, concise, and actionable
- If unsure, admit it and suggest consulting a doctor
- Never diagnose or prescribe medication
- IMPORTANT: Always respond in the SAME LANGUAGE as the user's question. If they ask in English, respond in English. If they ask in Bangla, respond in Bangla.

Format responses in a friendly, conversational tone."""

        self.medical_system_prompt_bn = """আপনি mySahara হেলথ অ্যাপের একজন সহায়ক চিকিৎসা স্বাস্থ্য সহায়ক।
আপনার ভূমিকা হল বাংলাদেশ এবং বিশ্বব্যাপী ব্যবহারকারীদের সঠিক, সহানুভূতিশীল এবং সাংস্কৃতিকভাবে সংবেদনশীল স্বাস্থ্য তথ্য প্রদান করা।

মূল নির্দেশিকা:
- প্রমাণ-ভিত্তিক স্বাস্থ্য তথ্য প্রদান করুন
- সহানুভূতিশীল এবং বোধগম্য হন
- সবসময় একটি দাবিত্যাগ অন্তর্ভুক্ত করুন যে আপনি পেশাদার চিকিৎসা পরামর্শ প্রতিস্থাপন করছেন না
- গুরুতর সমস্যার জন্য ব্যবহারকারীদের স্বাস্থ্যসেবা পেশাদারদের সাথে পরামর্শ করতে উৎসাহিত করুন
- বাংলাদেশী প্রসঙ্গে সাংস্কৃতিকভাবে সংবেদনশীল হন
- প্রতিক্রিয়া স্পষ্ট, সংক্ষিপ্ত এবং কার্যকর রাখুন
- অনিশ্চিত হলে স্বীকার করুন এবং ডাক্তারের পরামর্শ নেওয়ার পরামর্শ দিন
- কখনই রোগ নির্ণয় বা ওষুধ নির্ধারণ করবেন না
- গুরুত্বপূর্ণ: সবসময় ব্যবহারকারীর প্রশ্নের মতো একই ভাষায় উত্তর দিন। তারা ইংরেজিতে জিজ্ঞাসা করলে ইংরেজিতে উত্তর দিন। তারা বাংলায় জিজ্ঞাসা করলে বাংলায় উত্তর দিন।

বন্ধুত্বপূর্ণ, কথোপকথনমূলক সুরে প্রতিক্রিয়া ফরম্যাট করুন।"""

    def _get_system_prompt(self, language: str, use_medical_mode: bool = True) -> str:
        """
        Get appropriate system prompt based on language and mode.

        Args:
            language: Language code (en, bn)
            use_medical_mode: Whether to use medical assistant prompt

        Returns:
            System prompt string
        """
        if not use_medical_mode:
            return "You are a helpful AI assistant."

        if language == "bn":
            return self.medical_system_prompt_bn
        else:
            return self.medical_system_prompt_en

    def _detect_language(self, text: str) -> str:
        """
        Detect language of text (improved heuristic).

        Args:
            text: Input text

        Returns:
            Language code (en or bn)
        """
        # Check for Bengali Unicode characters
        bengali_chars = sum(1 for char in text if '\u0980' <= char <= '\u09FF')
        total_chars = len(text.replace(' ', '').replace('\n', ''))

        if total_chars > 0 and bengali_chars / total_chars > 0.2:  # Lowered threshold
            return "bn"
        return "en"

    async def chat_with_groq(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        model: str = "llama-3.3-8b-instant"
    ) -> Dict[str, Any]:
        """
        Chat using Groq API.

        Args:
            message: User message
            conversation_history: Previous conversation messages
            system_prompt: System prompt to use
            model: Groq model to use

        Returns:
            Dict containing response and metadata
        """
        if not self.groq_client:
            raise Exception("Groq client not initialized")

        try:
            start_time = time.time()

            # Build messages array
            messages = []

            # Add system prompt
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history)

            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })

            # Call Groq API
            response = self.groq_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                top_p=0.9,
                stream=False
            )

            processing_time = time.time() - start_time

            assistant_message = response.choices[0].message.content

            logger.info(f"Groq chat completed in {processing_time:.2f}s")

            return {
                "success": True,
                "message": assistant_message,
                "model_used": model,
                "processing_time": processing_time,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }

        except Exception as e:
            logger.error(f"Groq chat failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def chat_with_gemini(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chat using Gemini API as fallback.

        Args:
            message: User message
            conversation_history: Previous conversation messages
            system_prompt: System prompt to use

        Returns:
            Dict containing response and metadata
        """
        if not self.gemini_model:
            raise Exception("Gemini client not initialized")

        try:
            start_time = time.time()

            # Build prompt with history
            full_prompt = ""

            if system_prompt:
                full_prompt += f"{system_prompt}\n\n"

            if conversation_history:
                for msg in conversation_history:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    full_prompt += f"{role}: {msg['content']}\n"

            full_prompt += f"User: {message}\nAssistant:"

            # Generate response
            response = self.gemini_model.generate_content(full_prompt)

            processing_time = time.time() - start_time

            assistant_message = response.text

            logger.info(f"Gemini chat completed in {processing_time:.2f}s")

            return {
                "success": True,
                "message": assistant_message,
                "model_used": "gemini-1.5-flash",
                "processing_time": processing_time
            }

        except Exception as e:
            logger.error(f"Gemini chat failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def chat(
        self,
        message: str,
        language: str = "en",
        conversation_history: Optional[List[Dict[str, str]]] = None,
        use_medical_mode: bool = True,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main chat method with automatic fallback.

        Args:
            message: User message
            language: Language code
            conversation_history: Previous messages
            use_medical_mode: Use medical assistant mode
            context: Additional context

        Returns:
            Dict containing response and metadata
        """
        # Auto-detect language if not specified
        if not language or language == "auto":
            language = self._detect_language(message)

        # Get system prompt
        system_prompt = self._get_system_prompt(language, use_medical_mode)

        # Add explicit language instruction
        if language == "en":
            system_prompt += "\n\nIMPORTANT: The user's message is in English. You MUST respond in English only."
        else:
            system_prompt += "\n\nগুরুত্বপূর্ণ: ব্যবহারকারীর বার্তা বাংলায়। আপনাকে অবশ্যই শুধুমাত্র বাংলায় উত্তর দিতে হবে।"

        # Add context to system prompt if provided
        if context:
            context_str = "\n\nAdditional Context:\n"
            for key, value in context.items():
                context_str += f"- {key}: {value}\n"
            system_prompt += context_str

        # Try Groq first
        if self.groq_client:
            result = await self.chat_with_groq(
                message=message,
                conversation_history=conversation_history,
                system_prompt=system_prompt
            )

            if result["success"]:
                result["language"] = language
                return result

            logger.warning("Groq failed, trying Gemini...")

        # Fallback to Gemini
        if self.gemini_model:
            result = await self.chat_with_gemini(
                message=message,
                conversation_history=conversation_history,
                system_prompt=system_prompt
            )

            if result["success"]:
                result["language"] = language
                return result

        # Both failed
        return {
            "success": False,
            "error": "All AI services are unavailable",
            "language": language
        }

    async def create_nutrition_fitness_plan(
        self,
        request: "AINutritionFitnessRequest"
    ) -> Dict[str, Any]:
        """
        Generate a personalized nutrition, supplement, and exercise plan using an AI model.

        Args:
            request: An AINutritionFitnessRequest object with user's metrics and goals.

        Returns:
            A dictionary containing the structured nutrition, supplement, and exercise plans.
        """
        prompt = f"""Act as an expert AI Nutritionist and Fitness Coach specializing in Bangladeshi cuisine and locally available foods. Based on the user's data, create a comprehensive, personalized, and safe 7-day plan. 

The user's details are:
- Age: {request.age}
- Gender: {request.gender}
- Height: {request.height_cm} cm
- Weight: {request.weight_kg} kg
- Activity Level: {request.activity_level}
- Primary Goal: {request.goal}
- Dietary Preferences: {request.dietary_preferences or 'None'}
- Locally Available Foods: {request.available_local_foods or 'Standard Bangladeshi foods like rice, lentils (dal), fish, chicken, seasonal vegetables, and fruits.'}

Your task is to generate a structured JSON response with the following keys: 'nutrition_plan', 'supplement_plan', 'exercise_plan', and 'disclaimer'.

1.  **nutrition_plan**: 
    -   `daily_calories`: Estimated daily calorie target.
    -   `macronutrients`: A dictionary with `protein_g`, `carbs_g`, and `fat_g`.
    -   `daily_plans`: A list of 7 dictionaries, one for each day of the week. Each daily plan should contain:
        -   `day`: The name of the day (e.g., "Monday").
        -   `meals`: A list of 3-4 meals for that day. Each meal should be a dictionary with `meal` (e.g., Breakfast), `food` (suggest specific dishes with portion sizes, e.g., '1 cup rice, 100g fish curry'), `calories`, and `alternatives` (suggest a different meal option).

2.  **supplement_plan**:
    -   `recommendations`: A list of dictionaries, each with `supplement`, `dosage`, and `reason`. Only recommend common, safe supplements if they align with the user's goal. If no supplements are needed, provide an empty list.

3.  **exercise_plan**:
    -   `weekly_schedule`: A list of 7 dictionaries, one for each day of the week. Each daily plan should contain:
        -   `day`: The name of the day (e.g., "Monday").
        -   `activity`: A short description of the workout (e.g., "Upper Body Strength").
        -   `duration_minutes`: The total duration of the workout.
        -   `exercises`: A list of specific exercises for that day (e.g., ["Push-ups", "Dumbbell Rows", "Overhead Press"]).
    -   `progression_advice`: A short paragraph on how the user can progressively increase the difficulty of their workouts over time.

4.  **disclaimer**: Include the following text verbatim: "This is an AI-generated plan. Consult with a qualified healthcare provider and fitness professional before making any changes to your diet or exercise routine."

Provide ONLY the JSON response. Do not include any other text or markdown formatting.
"""

        # For this specific task, we expect a JSON response, so we'll use a model that is good at it.
        # Llama 3.1 is a good choice for this.
        if not self.groq_client:
            raise Exception("Groq client not initialized for this feature.")

        try:
            start_time = time.time()
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert AI Nutritionist and Fitness Coach that provides responses in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2048,
                top_p=0.9,
                response_format={"type": "json_object"}
            )

            processing_time = time.time() - start_time
            logger.info(f"AI nutrition & fitness plan generated in {processing_time:.2f}s")

            content = response.choices[0].message.content
            # The response should be a JSON string, so we parse it.
            import json
            plan_data = json.loads(content)

            return {
                "success": True,
                **plan_data
            }

        except Exception as e:
            logger.error(f"Error generating AI nutrition & fitness plan: {e}")
            return {
                "success": False,
                "error": "Failed to generate the plan. The AI model may be temporarily unavailable or the request could not be processed."
            }

    async def analyze_symptoms(
        self,
        symptoms: List[str],
        duration: Optional[str] = None,
        severity: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze symptoms and provide health insights.

        Args:
            symptoms: List of symptoms
            duration: Duration of symptoms
            severity: Severity level
            additional_info: Additional patient information

        Returns:
            Dict containing analysis and recommendations
        """
        # Build analysis prompt
        prompt = f"""Analyze the following symptoms and provide health insights:

Symptoms: {', '.join(symptoms)}"""

        if duration:
            prompt += f"\nDuration: {duration}"

        if severity:
            prompt += f"\nSeverity: {severity}"

        if additional_info:
            prompt += f"\n\nAdditional Information:"
            for key, value in additional_info.items():
                prompt += f"\n- {key}: {value}"

        prompt += """

Please provide:
1. Possible conditions (with probability if possible)
2. Risk level assessment (low/medium/high)
3. Recommendations for care
4. Whether urgent medical attention is needed

Remember to include appropriate medical disclaimers."""

        # Use chat method with medical mode
        result = await self.chat(
            message=prompt,
            language="en",
            use_medical_mode=True
        )

        if result["success"]:
            # Parse response to extract structured data
            # This is simplified - could be enhanced with more sophisticated parsing
            return {
                "success": True,
                "analysis": result["message"],
                "model_used": result.get("model_used"),
                "processing_time": result.get("processing_time")
            }
        else:
            return result

    async def generate_health_tips(
        self,
        category: Optional[str] = None,
        language: str = "en",
        personalized: bool = False,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate health tips.

        Args:
            category: Health category
            language: Language for tips
            personalized: Whether to personalize
            user_profile: User profile for personalization

        Returns:
            Dict containing health tips
        """
        prompt = "Provide 5 helpful health tips"

        if category:
            prompt += f" about {category}"

        if personalized and user_profile:
            prompt += f"\n\nPersonalize for: {user_profile}"

        prompt += "\n\nFormat as numbered list with brief explanations."

        result = await self.chat(
            message=prompt,
            language=language,
            use_medical_mode=True
        )

        return result

    async def predict_health_risks(
        self,
        health_metrics: Dict[str, Any],
        medical_history: Optional[List[str]] = None,
        lifestyle_factors: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Predict health risks based on metrics and history.

        Args:
            health_metrics: Current health metrics
            medical_history: Past medical conditions
            lifestyle_factors: Lifestyle information

        Returns:
            Dict containing risk predictions
        """
        prompt = f"""Analyze the following health data and predict potential health risks:

Health Metrics:
{self._format_dict(health_metrics)}"""

        if medical_history:
            prompt += f"\n\nMedical History: {', '.join(medical_history)}"

        if lifestyle_factors:
            prompt += f"\n\nLifestyle Factors:\n{self._format_dict(lifestyle_factors)}"

        prompt += """

Please provide:
1. Potential health risks (with probability estimates)
2. Risk factors identified
3. Preventive measures and recommendations
4. Timeline for potential conditions

Include appropriate disclaimers about limitations of AI predictions."""

        result = await self.chat(
            message=prompt,
            language="en",
            use_medical_mode=True
        )

        return result

    def _format_dict(self, data: Dict[str, Any], indent: int = 0) -> str:
        """
        Format dictionary for readable prompt inclusion.

        Args:
            data: Dictionary to format
            indent: Indentation level

        Returns:
            Formatted string
        """
        lines = []
        prefix = "  " * indent

        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(self._format_dict(value, indent + 1))
            else:
                lines.append(f"{prefix}{key}: {value}")

        return "\n".join(lines)


# Singleton instance of the AI service
_ai_service_instance: Optional[AIService] = None

def get_ai_service() -> AIService:
    """
    Get a singleton instance of the AIService.
    This is used for dependency injection in FastAPI.

    Returns:
        An instance of the AIService.
    """
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance
