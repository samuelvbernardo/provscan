import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from omr.services.pipeline import process_image

if __name__ == "__main__":
    process_image("omr/gabarito_bolhas_vazias.jpg")