import logging
# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('code_review.log'),
        logging.StreamHandler()  # Still prints to console
    ]
)

logger = logging.getLogger(__name__)