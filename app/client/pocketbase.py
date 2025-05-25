import os
from typing import Dict, Any
from pocketbase import PocketBase
from dotenv import load_dotenv

load_dotenv()

class PocketBaseClient:
    def __init__(self):
        self.pb = PocketBase(os.getenv("POCKETBASE_URL", "http://127.0.0.1:8090"))
        # Authenticate admin if credentials provided
        admin_email = os.getenv("POCKETBASE_ADMIN_EMAIL")
        admin_password = os.getenv("POCKETBASE_ADMIN_PASSWORD")
        if admin_email and admin_password:
            self.pb.admins.auth_with_password(admin_email, admin_password)

    def create_assessment(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new assessment record in PocketBase
        
        Args:
            assessment_data: Dictionary containing assessment data
            
        Returns:
            Created record data
        """
        try:
            record = self.pb.collection('assessments').create(assessment_data)
            return record.dict()
        except Exception as e:
            raise Exception(f"Failed to create assessment: {str(e)}")

    def get_assessment(self, assessment_id: str) -> Dict[str, Any]:
        """
        Retrieve an assessment by ID
        
        Args:
            assessment_id: ID of the assessment to retrieve
            
        Returns:
            Assessment record data
        """
        try:
            record = self.pb.collection('assessments').get(assessment_id)
            return record.dict()
        except Exception as e:
            raise Exception(f"Failed to get assessment: {str(e)}")

# Create singleton instance
pb_client = PocketBaseClient()
