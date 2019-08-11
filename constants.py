# API response messages
NEW_CANDIDATE_SUCCESS = 'Candidate successfully added'
MISSING_PAYLOAD_DATA = 'Incomplete payload data in request: %s'
SERVER_ERROR = 'Listing failed due to server side error: %s'
INVALID_CANDIDATE_OR_POLL_CLOSED = 'Listing is not a candidate. Cannot set data hash until it is.'
NOT_DATATRUST = 'Server is not the datatrust, unable to send data hash'

# Database response messages
DB_SUCCESS = 'Database transaction completed successfully'
ITEM_NOT_FOUND = 'No results returned'
DB_ERROR = 'Error reading/writing to database'

# Protocol constants
PROTOCOL_APPLICATION = 1
PROTOCOL_REGISTRATION = 4
CANDIDATE_ADDED = 'CandidateAdded'

# S3 Namespaces
S3_CANDIDATE = 'candidate'
S3_LISTING = 'listing'