# Global settings - All configurations are centralized in one file
class Config:
    # Data paths
    INPUT_DIR = "data/input"
    OUTPUT_DIR = "data/output"
    
    # Sampling settings
    SAMPLE_SIZE_PER_CATEGORY = 50
    
    # API settings
    API_PROVIDER = "deepseek"
    API_KEY = "your-api-key"
    BATCH_SIZE = 10
    MAX_WORKERS = 5
    
    # Unified field mapping configuration - defined in the order of Excel columns
    # Use None to indicate that the column should be discarded and not saved to manual_fields
    # The first column is telex by default, starting from the second column here
    CATEGORY_FIELDS = {
        'runway': [
            'telex',          # Column 2: Primary key (discard)
            None,             # Column 3: Affected area (keep)
            'affect_region',
            'airport',        # Column 4: Airport code (keep)
            'flight_type',    # Column 5: Flight type (keep)
            'runway',         # Column 6: Runway (keep)
            'status_type',    # Column 7: Restriction type (keep)
            'ppr',            # Column 8: Prior permission required (discard)
            'aip',            # Column 9: AIP reference (discard)
            'tora',           # Column 10: Takeoff run available (discard)
            'toda',           # Column 11: Takeoff distance available (discard)
            'asda',           # Column 12: Accelerate-stop distance available (discard)
            'lda',            # Column 13: Landing distance available (discard)
            'distance_chg'    # Column 14: Distance change (discard)
        ],
        'taxiway': [
            'telex',          # Column 2: Primary key (discard)
            None,             # Column 3: Affected area (keep)
            'status_type',    # Column 7: Restriction type (keep)
            'airport',        # Column 4: Airport code (keep)
            'taxiway',        # Column 5: Flight type (keep)
            'section',        # Column 8: Prior permission required (discard)
            'intersection_with'           
        ],
        'airway': [
            'telex',          # Column 2: Primary key (discard)
            None,             # Column 3: Affected area (keep)
            'route',          # Column 3: Affected area (keep)
            'start',          # Column 4: Airport code (keep)
            'end',            # Column 5: Flight type (keep)
            'directional',    # Column 6: Airspace type (keep)
            'height_detail',  # Column 7: Coordinates (discard, too complex)
            'atc',
            'fpl',
            'change_info'
        ],
        'airport': [
            'telex',          # Column 2: Primary key (discard)
            None,             # Column 3: Affected area (keep)
            'airport',        # Column 2: Primary key (discard)
            'restriction_Type', # Column 5: Flight type (keep)
            'flight_type',    # Column 6: Airport status (keep)
            'affect_region',  # Column 3: Affected area (keep)
            'Diversion_Restriction',
            'aip',            # Column 9: AIP reference (discard)
            'ppr',
            'fuel',           # Column 4: Airport code (keep)
            'industrialaction', # Column 5: Flight type (keep)
            'powersupply',    # Column 8: Prior permission required (discard)
        ],
        'navigation': [
            None,             # Column 2: Primary key (discard)
            'telex',          # Column 3: Affected area (keep)
            'airport',        # Column 4: Airport code (keep)
            'runway',         # Column 5: Flight type (keep)
            'navaid_id',      # Column 6: Navigation aid (keep)
            'navaid_type',    # Column 7: Frequency (keep)
        ],
        'light': [ 
            None,  
            'telex',          # Column 1: NOTAM text
            'airport',        # Column 2: Airport code
            'runway',         # Column 3: Runway
            'lightcategory',  # Column 4: Light category
            'ilscategory',    # Column 5: ILS category
            'unavailable/downgrade', # Column 6: Unavailable/Downgrade status
            'als',            # Column 7: ALS
            'distance',       # Column 8: Distance
            'percentage'      # Column 9: Percentage
        ],
        'procedure': [
            None,             # Column 3: Affected area (keep)
            'telex',          # Column 2: Primary key (discard)
            'airport',        # Column 4: Airport code (keep)
            'runway',         # Column 5: Procedure type (keep)
            'procedure_type', # Column 6: Procedure name (keep)
            'Chart',
            'procedure_name', # Column 7: Status type (keep)
            'aip',            # Column 8: AIP reference (discard)
            None,             # Column 3: Affected area (keep)
            None,             # Column 3: Affected area (keep)
            None
        ],
        'stand': [
            'telex',          # Column 3: Affected area (keep)
            None,             # Column 2: Primary key (discard)
            'stand_split_info', # Column 3: Split information (keep)
            'stand_status',   # Column 4: Status (keep)
            'airport',        # Column 4: Airport code (keep)
        ],
        'standard': [
            None,
            'telex',          # Column 3: Affected area (keep)
            'airport',        # Column 4: Airport code (keep)
            'runway',         # Column 3: Split information (keep)
            'procedure_name', # Column 4: Status (keep)
            'approach_type',  # Column 4: Airport code (keep)
            'aircraft_category', # Column 4: Airport code (keep)
            'minima_type',    # Column 4: Airport code (keep)
            'minima_value',   # Column 4: Airport code (keep)
            'notam_type',     # Column 4: Airport code (keep)
            None,             # Column 2: Primary key (discard)
            None,             # Column 2: Primary key (discard)
            None,             # Column 2: Primary key (discard)
            None,             # Column 2: Primary key (discard)
            None,             # Column 2: Primary key (discard)
            None,             # Column 2: Primary key (discard)
        ],
        'area': [
            None,             # Column 3: Affected area (keep)
            'area_type',      # Column 2: Primary key (discard)
            'area_summary',   # Column 4: Airport code (keep)
            'height_detail',  # Column 5: Procedure type (keep)
            None,
            'atc',
            'fpl',
            None,
            'telex',
            None
        ],
        'RVR': [
            None,             # Column 3: Affected area (keep)
            'telex',          # Column 2: Primary key (discard)
            'airport',        # Column 4: Airport code (keep)
            'runway',         # Column 5: Procedure type (keep)
            'touchdown_zone_unavailable', # Column 6: Procedure name (keep)
            'midpoint_unavailable',       # Column 7: Status type (keep)
            'stop_end_unavailable'        # Column 8: AIP reference (discard)
        ]
    }