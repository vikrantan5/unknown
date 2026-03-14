"""
Groq AI Service for automatic evaluation of subjective answers
"""
from groq import Groq
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class GroqEvaluationService:
    """Service for evaluating subjective answers using Groq AI"""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"
    
    def evaluate_subjective_answer(self, question_text, model_answer, student_answer, max_marks):
        """
        Evaluate a subjective answer using Groq AI
        
        Args:
            question_text: The question asked
            model_answer: The correct/model answer
            student_answer: Student's submitted answer
            max_marks: Maximum marks for this question
            
        Returns:
            dict: {
                'marks': float,
                'feedback': str,
                'percentage': float
            }
        """
        try:
            logger.info(f"Starting Groq evaluation for question (max_marks={max_marks})")
            # Create a comprehensive prompt for evaluation
            prompt = f"""You are an expert examiner evaluating a student's answer. Please evaluate the following answer objectively and fairly.

QUESTION:
{question_text}

MODEL ANSWER (Reference):
{model_answer}

STUDENT'S ANSWER:
{student_answer}

MAXIMUM MARKS: {max_marks}

Please evaluate the student's answer based on:
1. Correctness and accuracy of information
2. Completeness of the answer
3. Understanding of the concept
4. Clarity and coherence

Provide your evaluation in the following format:
MARKS: [number out of {max_marks}]
FEEDBACK: [Detailed constructive feedback explaining why marks were awarded or deducted, highlighting strengths and areas for improvement]

Be fair, objective, and constructive in your evaluation."""

            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert examiner who evaluates student answers fairly and objectively. You provide constructive feedback to help students learn."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.3,  # Lower temperature for more consistent evaluation
                max_tokens=1000,
            )
            
            # Parse the response
            response_text = chat_completion.choices[0].message.content
            
            # Extract marks and feedback
            marks = self._extract_marks(response_text, max_marks)
            feedback = self._extract_feedback(response_text)
            percentage = (marks / max_marks) * 100 if max_marks > 0 else 0
            
            return {
                'marks': marks,
                'feedback': feedback,
                'percentage': round(percentage, 2),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Groq AI evaluation failed: {str(e)}")
            return {
                'marks': 0,
                'feedback': f"Auto-evaluation failed: {str(e)}. Please manually review this answer.",
                'percentage': 0,
                'success': False
            }
    
    def _extract_marks(self, response_text, max_marks):
        """Extract marks from the AI response"""
        try:
            import re
            
            # Look for "MARKS:" pattern - split by newline, not space
            lines = response_text.split('\n')
            for line in lines:
                if 'MARKS:' in line.upper():
                    # Extract the number
                    marks_str = line.split(':', 1)[1].strip()
                    
                    # Handle formats like "8/10" or "8 out of 10" or just "8"
                    if '/' in marks_str:
                        marks = float(marks_str.split('/')[0].strip())
                    elif 'out of' in marks_str.lower():
                        marks = float(marks_str.split('out of')[0].strip())
                    else:
                        # Try to extract just the number - FIXED REGEX
                        numbers = re.findall(r'\d+\.?\d*', marks_str)
                        if numbers:
                            marks = float(numbers[0])
                        else:
                            marks = 0
                    
                    # Ensure marks don't exceed max_marks
                    marks = max(0, min(marks, max_marks))
                    logger.info(f"Extracted marks: {marks}/{max_marks}")
                    return marks
            
            # If no marks found in MARKS: pattern, try to extract first number
            logger.warning("No MARKS: pattern found, trying to extract first number")
            numbers = re.findall(r'\d+\.?\d*', response_text)
            if numbers:
                marks = max(0, min(float(numbers[0]), max_marks))
                logger.info(f"Extracted marks from first number: {marks}/{max_marks}")
                return marks
            
            # If no marks found, return 0
            logger.warning("No marks found in response, returning 0")
            return 0
            
        except Exception as e:
            logger.error(f"Failed to extract marks from response: {str(e)}")
            return 0
    
    def _extract_feedback(self, response_text):
        """Extract feedback from the AI response"""
        try:
            # Look for "FEEDBACK:" pattern
            if 'FEEDBACK:' in response_text.upper():
                parts = response_text.split('FEEDBACK:', 1)
                if len(parts) > 1:
                    return parts[1].strip()
            
            # If no specific feedback section, return the whole response
            return response_text.strip()
            
        except Exception as e:
            logger.error(f"Failed to extract feedback from response: {str(e)}")
            return "Feedback extraction failed. Please review manually."
    
    def batch_evaluate_subjective_answers(self, answers_data):
        """
        Evaluate multiple subjective answers in batch
        
        Args:
            answers_data: List of dicts with keys: question_text, model_answer, student_answer, max_marks
            
        Returns:
            List of evaluation results
        """
        results = []
        for data in answers_data:
            result = self.evaluate_subjective_answer(
                question_text=data['question_text'],
                model_answer=data['model_answer'],
                student_answer=data['student_answer'],
                max_marks=data['max_marks']
            )
            results.append(result)
        
        return results


# Singleton instance
_groq_service = None

def get_groq_service():
    """Get or create Groq evaluation service instance"""
    global _groq_service
    if _groq_service is None:
        _groq_service = GroqEvaluationService()
    return _groq_service