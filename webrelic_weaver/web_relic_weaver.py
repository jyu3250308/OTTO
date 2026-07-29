import datetime
import random
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw
import os

def generate_mock_html_relic():
    """
    Simulates retrieving an old 'relic' HTML page from a predefined set.
    Provides diverse content for analysis.
    """
    print("  [Step 1/4] Generating mock HTML content...")
    mock_pages = [
        """
        <html>
        <head><title>Welcome to the Web Frontier!</title></head>
        <body bgcolor="#CCCCCC">
            <center>
                <h1>My Awesome Page</h1>
                <p>Hello world! This is my first webpage from 1999.</p>
                <img src="images/broken_cat.gif" alt="Cute Cat" border="0">
                <a href="about.html">Learn more about me</a><br>
                <a href="#">Old link reference</a>
                <p>Visit my <font color="red">guestbook</font> soon!</p>
                <ul><li>Item 1</li><li>Item 2</li></ul>
            </center>
            <marquee>Under Construction!</marquee>
        </body>
        </html>
        """,
        """
        <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
            <title>My Personal Homepage</title>
            <style type="text/css">
                body { font-family: Arial, sans-serif; background-color: #000080; color: #FFFFFF; }
                a { color: #00FFFF; }
            </style>
        </head>
        <body>
            <table width="100%" border="0" cellspacing="0" cellpadding="5">
                <tr><td align="center"><h2>Welcome to the Cyber Frontier</h2></td></tr>
            </table>
            <p>Here you'll find exciting content about my hobbies.</p>
            <img src="/assets/non_existent.jpg" alt="Cool Image">
            <a href="mailto:webmaster@example.com">Contact Me</a>
            <hr>
            <p><small>&copy; 1998 Web Weaver</small></p>
            <!-- This is an old comment -->
        </body>
        </html>
        """
    ]
    return random.choice(mock_pages)

def analyze_relic_html(html_content: str) -> dict:
    """
    Analyzes the provided HTML content for structural elements, potential broken links,
    and text patterns, returning a dictionary of findings.

    Args:
        html_content (str): The HTML string to be analyzed.

    Returns:
        dict: A dictionary containing analysis results like tag counts, broken element counts, and text density.
    """
    print("  [Step 2/4] Analyzing relic HTML content...")
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
    except Exception as e:
        print(f"    Error parsing HTML: {e}")
        return {"tag_count": 0, "unique_tags": 0, "broken_elements_count": 0, "text_density": 0}

    tag_counts = {}
    for tag in soup.find_all(True):
        tag_counts[tag.name] = tag_counts.get(tag.name, 0) + 1

    broken_elements_count = 0
    # Heuristic for 'broken' or internal reference links
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if href in ['#', '', 'javascript:void(0);'] or (href.startswith('/') and not href.startswith('//')):
            broken_elements_count += 1
    # Heuristic for 'broken' image paths
    for img_tag in soup.find_all('img', src=True):
        src = img_tag['src']
        if src.startswith(('images/', '/assets/', 'http://example.com/broken/')):
            broken_elements_count += 1

    text_content = " ".join(soup.stripped_strings)
    unique_words_count = len(set(text_content.lower().split()))

    print(f"    - Detected {len(tag_counts)} unique HTML tags. Total tags: {sum(tag_counts.values())}")
    print(f"    - Identified approximately {broken_elements_count} potentially 'broken' links/assets.")
    print(f"    - Calculated unique text word density: {unique_words_count} words.")

    return {
        "tag_count": sum(tag_counts.values()),
        "unique_tags": len(tag_counts),
        "broken_elements_count": broken_elements_count,
        "text_density": unique_words_count
    }

def generate_web_fossil_art(analysis_data: dict, output_dir: str = ".") -> str:
    """
    Generates a generative art piece based on the HTML analysis data, simulating an 'ancient web fossil'.
    Saves the artwork as a PNG image with a timestamp.

    Args:
        analysis_data (dict): A dictionary containing the results from HTML analysis.
        output_dir (str): Directory to save the generated image.

    Returns:
        str: The full path to the generated image file.
    """
    print("  [Step 3/4] Generating web fossil art from analysis data...")
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(image)

    palette = [
        (0, 51, 102), (204, 204, 204), (255, 0, 0), (0, 153, 0), (255, 255, 102)
    ]

    num_elements = analysis_data['tag_count'] // 5 + analysis_data['unique_tags'] * 2
    broken_elements = analysis_data['broken_elements_count']
    text_density_factor = analysis_data['text_density'] // 50

    # Draw abstract 'structural' lines/rectangles
    for i in range(min(num_elements, 100)):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        color = random.choice([palette[0], palette[1]])
        draw.line([(x1, y1), (x2, y2)], fill=color, width=random.randint(1, 3))

    # Draw 'text pattern' blocks
    for i in range(min(text_density_factor, 50)):
        x, y = random.randint(0, width), random.randint(0, height)
        block_width, block_height = random.randint(10, 50), random.randint(5, 20)
        draw.rectangle([x, y, x + block_width, y + block_height], fill=palette[1])

    # Highlight 'broken elements' with a distinct pattern
    for i in range(min(broken_elements, 30)):
        x_center, y_center = random.randint(0, width), random.randint(0, height)
        radius = random.randint(5, 15)
        draw.ellipse([x_center - radius, y_center - radius, x_center + radius, y_center + radius], outline=palette[2], width=2)
        draw.line([(x_center - radius, y_center - radius), (x_center + radius, y_center + radius)], fill=palette[2], width=1)
        draw.line([(x_center + radius, y_center - radius), (x_center - radius, y_center + radius)], fill=palette[2], width=1)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"web_fossil_art_{timestamp}.png"
    output_path = os.path.join(output_dir, output_filename)

    try:
        image.save(output_path)
        print(f"    Web fossil art successfully saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f"    Error saving image to {output_path}: {e}")
        return ""

if __name__ == "__main__":
    print("\n[Program Start] Web Relic Weaver activated.")
    print("-------------------------------------------")

    try:
        # 1. Generate mock old HTML content
        html_content = generate_mock_html_relic()

        # 2. Analyze the generated HTML
        analysis_results = analyze_relic_html(html_content)

        # 3. Generate generative art based on analysis
        output_image_path = generate_web_fossil_art(analysis_results)

        print("-------------------------------------------")
        print(f"[Program End] Web Relic Weaver completed. Output image: {output_image_path or 'None'}")

    except Exception as e:
        print(f"\n[Program Error] An unexpected error occurred: {e}")
        print("-------------------------------------------")

