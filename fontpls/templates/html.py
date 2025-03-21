"""
HTML template generation for fontpls.
"""
from collections import defaultdict


def create_demo_html(font_metadata):
    """
    Create an HTML demo page that showcases all downloaded fonts with h1-h6 and p tags.

    Args:
        font_metadata (dict): Dictionary of font metadata

    Returns:
        str: HTML content for the demo page
    """
    # Group fonts by family
    families = defaultdict(list)
    for url, metadata in font_metadata.items():
        families[metadata["family"]].append(
            {
                "style": metadata["style"],
                "weight": metadata.get("weight", "400"),
                "font_style": metadata.get("font_style", "normal"),
                "filename": metadata["filename"],
            }
        )

    # Create HTML header
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Font Demo</title>
  <link rel="stylesheet" href="fonts.css">
  <style>
    body {
      font-family: system-ui, -apple-system, sans-serif;
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem;
      line-height: 1.5;
    }

    .font-section {
      margin-bottom: 4rem;
      padding: 2rem;
      border: 1px solid #eee;
      border-radius: 8px;
    }

    .sample-text {
      margin-top: 1rem;
    }

    .metadata {
      color: #666;
      font-size: 0.875rem;
      margin-bottom: 1rem;
    }
  </style>
</head>
<body>
  <h1>Font Demo Page</h1>
"""

    # Create a section for each font family
    for family, variants in families.items():
        for variant in variants:
            style = variant["style"]
            f"font-{family.lower().replace(' ', '-')}-{style.lower().replace(' ', '-')}"

            html += f"""
  <div class="font-section">
    <h2>{family} {style}</h2>
    <div class="metadata">
      Font Weight: {variant['weight']} | Font Style: {variant['font_style']} | Filename: {variant['filename']}
    </div>
    <div style="font-family: '{family}', sans-serif; font-weight: {variant['weight']}; font-style: {variant['font_style']};">
      <h1>Heading 1 - {family} {style}</h1>
      <h2>Heading 2 - {family} {style}</h2>
      <h3>Heading 3 - {family} {style}</h3>
      <h4>Heading 4 - {family} {style}</h4>
      <h5>Heading 5 - {family} {style}</h5>
      <h6>Heading 6 - {family} {style}</h6>

      <div class="sample-text">
        <p>This is a paragraph in {family} {style}. The quick brown fox jumps over the lazy dog.</p>
        <p>0123456789 !@#$%^&*()_+{{}}|:"<>?~</p>
        <p>const example = () => {{ return "This is a code example"; }};</p>
      </div>
    </div>
  </div>
"""

    # Close HTML document
    html += """</body>
</html>"""

    return html
