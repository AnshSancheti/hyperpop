from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw
import datetime, os, pyautogui, pytesseract

class ImageToTextReader:
    def take_screenshot(self, x, y, width, height):
        """
        Capture a specific region of the screen.
        
        Args:
            x (int): The x-coordinate of the top-left corner of the region
            y (int): The y-coordinate of the top-left corner of the region
            width (int): The width of the region to capture
            height (int): The height of the region to capture
        
        Returns:
            Image: The screenshot of the specified region
        """    
        # Take a screenshot of the specified region
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        
        # Save the screenshot to disk for debugging
        #curtime = datetime.datetime.now()
        #screenshot.save(f'./screenshot_{curtime}.png')
        #Image.open(f'./screenshot_{curtime}.png').show()

        return screenshot
    
    def preprocess_image(self, screenshot) -> Image:
        """
        Preprocess an image before extracting text from it.
        
        Args:
            image (Image): The image to preprocess
        
        Returns:
            Image: The preprocessed image
        """
        screenshot = screenshot.convert('RGB')

        # Enhance contrast 
        enhancer = ImageEnhance.Contrast(screenshot)
        screenshot = enhancer.enhance(2.0)
        screenshot = ImageOps.invert(screenshot)
        
        # Enhance brightness
        enhancer = ImageEnhance.Brightness(screenshot)
        screenshot = enhancer.enhance(1.3)
        screenshot = screenshot.point(lambda x: 0 if x < 10 else 255)
        screenshot = screenshot.filter(ImageFilter.MedianFilter(size=3))
        screenshot = screenshot.convert('L')

        return screenshot

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
            screenshot = self.take_screenshot(x, y, width, height)
            screenshot = self.preprocess_image(screenshot)
            
            # Extract text from the image using settings from pytesseract
            # https://pypi.org/project/pytesseract/
            text = pytesseract.image_to_string(
                screenshot, 
                config=f"-c tessedit_char_whitelist={charwhitelist} --psm 7", 
                nice=1)
            
            return text.strip()
        
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

    def extract_text_from_screenshot(self, filepath) -> str:
        """
        Helper functiuon to confirm the OCR is working as expected.
        """
        try:
            screenshot = Image.open(filepath)
            screenshot = self.preprocess_image(screenshot)

            # Save the screenshot to disk for debugging
            #curtime = datetime.datetime.now()
            #screenshot.save(f'./screenshot_{curtime}.png')
            #Image.open(f'./screenshot_{curtime}.png').show()
            
            # Extract text from the image using settings from pytesseract
            # https://pypi.org/project/pytesseract/
            text = pytesseract.image_to_string(
                screenshot, 
                config=f"-c tessedit_char_whitelist=0123456789/ --psm 7", 
                nice=1)

            return text.strip()       
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

    def get_text_regions(self, image):
        """
        Get bounding boxes for detected text and return both coordinates and characters.
        
        Args:
            image: PIL Image object
        Returns:
            list of dicts containing character and its bounding box
        """
        boxes = pytesseract.image_to_boxes(image)
        regions = []
        for box in boxes.splitlines():
            parts = box.split()
            if len(parts) >= 6:  # Ensure we have all required parts
                char = parts[0]
                x1, y1, x2, y2 = map(int, parts[1:5])
                # Note: pytesseract returns coordinates from bottom-left origin
                # Convert to top-left origin
                height = image.height
                regions.append({
                    'char': char,
                    'box': (x1, height - y2, x2, height - y1)
                })
        return regions
    
    def visualize_text_regions(self, image_path, output_path=None):
        """
        Draw boxes around detected text regions and optionally save the result.
        
        Args:
            image_path: Path to input image or PIL Image object
            output_path: Optional path to save annotated image
        """
        # Load image if path is provided, otherwise assume PIL Image
        if isinstance(image_path, str):
            image = Image.open(image_path)
        else:
            image = image_path
        
        image = self.preprocess_image(image)

        # Create a copy for drawing
        draw_image = image.copy()
        draw = ImageDraw.Draw(draw_image)
        
        # Get and draw regions
        regions = self.get_text_regions(image)
        
        # Draw boxes and labels
        for region in regions:
            box = region['box']
            char = region['char']
            
            # Draw rectangle
            draw.rectangle(box, outline='red', width=2)
            
            # Optional: Draw character label above box
            draw.text((box[0], box[1] - 10), char, fill='red')
        
        draw_image.show()

        # Save if output path provided
        if output_path:
            draw_image.save(output_path)
        
        return draw_image, regions


# Main function to test the ImageToTextReader class
if __name__ == '__main__':
    # Test the OCR on a set of screenshots, run from root directory
    reader = ImageToTextReader()
    for filename in os.listdir('./app/test_screenshots'):
        reader.visualize_text_regions(f'./app/test_screenshots/{filename}')
        text = reader.extract_text_from_screenshot(f'./app/test_screenshots/{filename}')
        print(f"Extracted text from {filename}: {text}")