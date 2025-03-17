import unittest
from unittest.mock import patch

# Import the functions/classes from your main code in frontend/app.py
from frontend.app import (
    extract_day,
    generate_schedule_response,
    generate_study_response,
    generate_personalized_content,
    generate_meal_plan,
    generate_combined_response,
    llm
)

def dummy_llm(prompt):
    return f"LLM response for: {prompt}"

class TestPersonalAssistant(unittest.TestCase):
    
    def test_extract_day(self):
        self.assertEqual(extract_day("What's my schedule for Friday?"), "Friday")
        self.assertEqual(extract_day("Tell me about monday plans"), "Monday")
        self.assertIsNone(extract_day("I don't mention any day"))
    
    @patch('frontend.app.llm', side_effect=dummy_llm)
    def test_schedule_response(self, mock_llm):
        test_day = "Monday"
        test_query = "What's my schedule for Monday?"
        response = generate_schedule_response(test_day, test_query)
        self.assertIn("Monday", response)
        self.assertIn("LLM response for:", response)
    
    @patch('frontend.app.llm', side_effect=dummy_llm)
    def test_study_response(self, mock_llm):
        test_query = "Show me the pdf study material."
        response = generate_study_response(test_query)
        self.assertIn("LLM response for:", response)
        self.assertIn("Study Material", response)
    
    @patch('frontend.app.llm', side_effect=dummy_llm)
    def test_personalized_content(self, mock_llm):
        test_query = "Create personalized content about my study goals."
        response = generate_personalized_content(test_query)
        self.assertIn("LLM response for:", response)
        self.assertIn("personal details", response)
    
    @patch('frontend.app.llm', side_effect=dummy_llm)
    def test_meal_plan(self, mock_llm):
        test_query = "I need a meal plan; my fridge has leftovers and I need to buy more."
        response = generate_meal_plan(test_query)
        self.assertIn("LLM response for:", response)
        self.assertIn("meal plan", response.lower())
    
    @patch('frontend.app.llm', side_effect=dummy_llm)
    def test_combined_response(self, mock_llm):
        test_query = "Tell me something interesting."
        response = generate_combined_response(test_query)
        self.assertIn("LLM response for:", response)

# -----------------------------
# Custom TestResult & TestRunner
# -----------------------------
class TickTestResult(unittest.TextTestResult):
    """Custom test result class that prints a tick mark for each successful test."""
    def addSuccess(self, test):
        super().addSuccess(test)
        self.stream.write(f"✅ {self.getDescription(test)}\n")

class TickTestRunner(unittest.TextTestRunner):
    """Custom test runner that uses our TickTestResult."""
    resultclass = TickTestResult

if __name__ == "__main__":
    # Run tests with our custom runner
    unittest.main(testRunner=TickTestRunner(verbosity=2))
