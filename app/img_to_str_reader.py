import pyautogui
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import datetime

class ImageToTextReader:
    def extract_text_from_region(self, x, y, width, height, charwhitelist='0123456789/') -> str:
        """
        Capture a specific region of the screen and extract text from it using OCR.
        
        Args:
            x (int): The x-coordinate of the top-left corner of the region
            y (int): The y-coordinate of the top-left corner of the region
            width (int): The width of the region to capture
            height (int): The height of the region to capture
        
        Returns:
            str: Extracted text from the captured region
        """
        try:
            # Take a screenshot of the specified region
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            
            # Convert the screenshot to a format pytesseract can process
            # We'll convert to RGB to ensure compatibility
            screenshot = screenshot.convert('RGB')

            # Enhance contrast 
            enhancer = ImageEnhance.Contrast(screenshot)
            contrast_enhanced = enhancer.enhance(2.0)
            contrast_enhanced = ImageOps.invert(contrast_enhanced)
            
            # Enhance brightness
            enhancer = ImageEnhance.Brightness(contrast_enhanced)
            final_image = enhancer.enhance(1.3)
            final_image = final_image.filter(ImageFilter.MedianFilter(size=3))
            final_image = final_image.point(lambda x: 0 if x < 10 else 255)
            final_image = final_image.convert('L') # Convert to grayscale
            
            # Save the screenshot to disk for debugging
            #curtime = datetime.datetime.now()
            #final_image.save(f'./screenshot_{curtime}.png')
            #Image.open(f'./screenshot_{curtime}.png').show()
            
            # Extract text from the image using settings from pytesseract
            # https://pypi.org/project/pytesseract/
            text = pytesseract.image_to_string(
                final_image, 
                config=f"-c tessedit_char_whitelist={charwhitelist} --psm 7", 
                nice=1)
            
            return text.strip()
        
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

    def extract_text_from_screenshot(self) -> str:
        """
        Helper functiuon to confirm the OCR is working as expected.
        """
        try:
            screenshot = Image.open(f'./screenshot.png')
            screenshot = screenshot.convert('RGB')

            # Enhance contrast 
            enhancer = ImageEnhance.Contrast(screenshot)
            contrast_enhanced = enhancer.enhance(2.0)
            contrast_enhanced = ImageOps.invert(contrast_enhanced)
            
            # Enhance brightness
            enhancer = ImageEnhance.Brightness(contrast_enhanced)
            final_image = enhancer.enhance(1.3)
            final_image = final_image.filter(ImageFilter.MedianFilter(size=3))
            final_image = final_image.point(lambda x: 0 if x < 10 else 255)
            final_image = final_image.convert('L') # Convert to grayscale
            
            # Save the screenshot to disk for debugging
            #curtime = datetime.datetime.now()
            #final_image.save(f'./screenshot_{curtime}.png')
            #Image.open(f'./screenshot_{curtime}.png').show()
            
            # Extract text from the image using settings from pytesseract
            # https://pypi.org/project/pytesseract/
            text = pytesseract.image_to_string(
                final_image, 
                config=f"-c tessedit_char_whitelist=0123456789/ --psm 6", 
                nice=1)
            
            return text.strip()
        
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

# Main function to test the ImageToTextReader class
if __name__ == '__main__':
    # Example usage
    reader = ImageToTextReader()
    text = reader.extract_text_from_screenshot()
    print(text)