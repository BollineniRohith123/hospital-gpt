import re
import json
import logging
from typing import Dict, List, Any

class HospitalGPT:
    def __init__(self, data_file: str = 'hospital_data.txt'):
        """
        Initialize HospitalGPT with hospital data from a text file.
        
        Args:
            data_file (str): Path to the hospital data text file
        """
        self.data_file = data_file
        self.hospital_data = self._load_hospital_data()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _load_hospital_data(self) -> str:
        """
        Load hospital data from the text file.
        
        Returns:
            str: Raw hospital data
        """
        try:
            with open(self.data_file, 'r') as file:
                return file.read()
        except FileNotFoundError:
            self.logger.error(f"Hospital data file not found: {self.data_file}")
            return ""
        except Exception as e:
            self.logger.error(f"Error loading hospital data: {e}")
            return ""

    def get_bed_availability(self, ward: str) -> Dict[str, Any]:
        """
        Retrieve bed availability for a specific ward.
        
        Args:
            ward (str): Name of the ward
        
        Returns:
            Dict with bed availability details
        """
        try:
            ward_pattern = rf"{ward} Ward: (\d+)/(\d+) beds occupied"
            match = re.search(ward_pattern, self.hospital_data, re.IGNORECASE)
            
            if match:
                occupied_beds, total_beds = map(int, match.groups())
                available_beds = total_beds - occupied_beds
                
                return {
                    "ward": ward,
                    "total_beds": total_beds,
                    "occupied_beds": occupied_beds,
                    "available_beds": available_beds,
                    "occupancy_rate": (occupied_beds / total_beds) * 100
                }
            
            return {"error": f"No data found for {ward} Ward"}
        
        except Exception as e:
            self.logger.error(f"Error retrieving bed availability: {e}")
            return {"error": "Unable to retrieve bed availability"}

    def get_death_rates(self, date: str) -> Dict[str, Any]:
        """
        Retrieve death rates for a specific date.
        
        Args:
            date (str): Date in YYYY-MM-DD format
        
        Returns:
            Dict with death rate details
        """
        try:
            death_rate_pattern = rf"{date}: (\d+) deaths"
            match = re.search(death_rate_pattern, self.hospital_data)
            
            if match:
                deaths = int(match.group(1))
                return {
                    "date": date,
                    "total_deaths": deaths
                }
            
            return {"error": f"No death rate data found for {date}"}
        
        except Exception as e:
            self.logger.error(f"Error retrieving death rates: {e}")
            return {"error": "Unable to retrieve death rates"}

    def get_staff_schedule(self, department: str, shift: str) -> Dict[str, Any]:
        """
        Retrieve staff schedule for a specific department and shift.
        
        Args:
            department (str): Department name
            shift (str): Shift name
        
        Returns:
            Dict with staff schedule details
        """
        try:
            schedule_pattern = (
                rf"{department} Department:\n"
                rf"- {shift} Shift \(.*?\):\n"
                r"((?:\s*\*\s*.*\n)*)"
            )
            match = re.search(schedule_pattern, self.hospital_data, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            
            if match:
                staff_list = [staff.strip().replace('* ', '') for staff in match.group(1).split('\n') if staff.strip()]
                
                return {
                    "department": department,
                    "shift": shift,
                    "staff": staff_list
                }
            
            return {"error": f"No staff schedule found for {department} Department, {shift} Shift"}
        
        except Exception as e:
            self.logger.error(f"Error retrieving staff schedule: {e}")
            return {"error": "Unable to retrieve staff schedule"}

    def get_treatment_outcomes(self, treatment: str, year: str) -> Dict[str, Any]:
        """
        Retrieve treatment outcomes for a specific treatment and year.
        
        Args:
            treatment (str): Treatment name
            year (str): Year of the study
        
        Returns:
            Dict with treatment outcome details
        """
        try:
            outcome_pattern = (
                rf"{treatment} Study \({year}\):\n"
                r"((?:- .*\n)*)"
            )
            match = re.search(outcome_pattern, self.hospital_data, re.IGNORECASE)
            
            if match:
                outcome_details = dict(
                    detail.strip().split(': ') 
                    for detail in match.group(1).split('\n') 
                    if detail.strip() and ': ' in detail
                )
                
                return {
                    "treatment": treatment,
                    "year": year,
                    "details": outcome_details
                }
            
            return {"error": f"No treatment outcome data found for {treatment} in {year}"}
        
        except Exception as e:
            self.logger.error(f"Error retrieving treatment outcomes: {e}")
            return {"error": "Unable to retrieve treatment outcomes"}

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query about hospital information.
        
        Args:
            query (str): User's query
        
        Returns:
            Dict with processed query results
        """
        query = query.lower()
        
        try:
            # Bed Availability Query
            if 'bed' in query and 'ward' in query:
                ward = re.search(r'(\w+) ward', query, re.IGNORECASE)
                if ward:
                    return self.get_bed_availability(ward.group(1))
            
            # Death Rates Query
            if 'death' in query and 'rate' in query:
                date = re.search(r'\d{4}-\d{2}-\d{2}', query)
                if date:
                    return self.get_death_rates(date.group(0))
            
            # Staff Schedule Query
            if 'staff' in query or 'schedule' in query:
                department = re.search(r'(\w+) department', query, re.IGNORECASE)
                shift = re.search(r'(\w+) shift', query, re.IGNORECASE)
                if department and shift:
                    return self.get_staff_schedule(department.group(1), shift.group(1))
            
            # Treatment Outcomes Query
            if 'treatment' in query or 'study' in query:
                treatment = re.search(r'(\w+) study', query, re.IGNORECASE)
                year = re.search(r'\d{4}', query)
                if treatment and year:
                    return self.get_treatment_outcomes(treatment.group(1), year.group(0))
            
            return {"error": "Unable to process query. Please rephrase or be more specific."}
        
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            return {"error": "An unexpected error occurred while processing your query."}

# Example usage
if __name__ == "__main__":
    hospital_gpt = HospitalGPT()
    
    # Example queries
    queries = [
        "How many beds are available in the General Ward?",
        "How many deaths occurred on 2024-01-30?",
        "Who is on duty in the Radiology Department during the General Shift?",
        "What were the outcomes of the Paracetamol Study in 2019?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = hospital_gpt.process_query(query)
        print(json.dumps(result, indent=2))
