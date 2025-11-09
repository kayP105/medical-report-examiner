import json
import os
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ValueAnalyzer:
    """Analyze medical test values against reference ranges"""

    def __init__(self):
        self.REFERENCE_RANGES = self._load_reference_ranges()

    def _load_reference_ranges(self) -> Dict:
        json_path = "data/reference_ranges.json"
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    ranges = json.load(f)
                logger.info(f"✅ Loaded {len(ranges)} reference ranges from JSON")
                return ranges
            else:
                logger.warning(f"⚠️ {json_path} not found")
                return {}
        except Exception as e:
            logger.error(f"Error loading reference ranges: {e}")
            return {}

    def analyze_value(
        self,
        term: str,
        value: float,
        unit: str = "",
        age: Optional[int] = None,
        gender: Optional[str] = None
    ) -> Dict:
        """Analyze if a value is within normal range"""

        # Get reference range
        if term not in self.REFERENCE_RANGES:
            return {
                'is_abnormal': False,
                'status': 'unknown',
                'message': f'Reference range for {term} not available'
            }

        ranges = self.REFERENCE_RANGES[term]
        # Robust gender logic
        g = (gender or '').lower()

        if g and g in ranges:
            ref_range = ranges[g]
        elif 'default' in ranges:
            ref_range = ranges['default']
        elif 'all' in ranges:
            ref_range = ranges['all']
        elif 'female' in ranges:
            ref_range = ranges['female']
        elif 'male' in ranges:
            ref_range = ranges['male']
        else:
            ref_range = list(ranges.values())[0]

        # Value comparison
        is_low = value < ref_range['min']
        is_high = value > ref_range['max']
        is_abnormal = is_low or is_high

        if is_low:
            status = 'low'
            message = f'{term} is below normal range (normal: {ref_range["min"]}-{ref_range["max"]} {ref_range["unit"]})'
        elif is_high:
            status = 'high'
            message = f'{term} is above normal range (normal: {ref_range["min"]}-{ref_range["max"]} {ref_range["unit"]})'
        else:
            status = 'normal'
            message = f'{term} is within normal range ({ref_range["min"]}-{ref_range["max"]} {ref_range["unit"]})'

        return {
            'is_abnormal': is_abnormal,
            'status': status,
            'message': message,
            'reference_range': f'{ref_range["min"]}-{ref_range["max"]} {ref_range["unit"]}'
        }
