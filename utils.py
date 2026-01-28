import os
import re
import zipfile
import xml.etree.ElementTree as ET
from docx import Document
from docx.oxml.ns import qn


def sanitize_filename(filename, max_length=50):
    name, ext = os.path.splitext(filename)
    safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', name)
    safe_name = re.sub(r'_+', '_', safe_name).strip('_')
    if not safe_name:
        safe_name = 'file'
    return safe_name[:max_length] + ext


def sanitize_path(path):
    dirname = os.path.dirname(path)
    filename = os.path.basename(path)
    return os.path.join(dirname, sanitize_filename(filename))


def extract_content_sequence(docx_path, temp_dir):
    doc = Document(docx_path)
    sequence = []
    image_map = {}
    rid_to_media = {}
    
    try:
        with zipfile.ZipFile(docx_path, 'r') as z:
            media_files = [n for n in z.namelist() if n.startswith('word/media/')]
            for i, name in enumerate(media_files):
                ext = os.path.splitext(name)[1]
                img_filename = f"img_{i:03d}{ext}"
                img_path = os.path.join(temp_dir, img_filename)
                with z.open(name) as src, open(img_path, 'wb') as dst:
                    dst.write(src.read())
                image_map[os.path.basename(name)] = img_path
            
            if 'word/_rels/document.xml.rels' in z.namelist():
                with z.open('word/_rels/document.xml.rels') as f:
                    tree = ET.parse(f)
                    root = tree.getroot()
                    ns = {'r': 'http://schemas.openxmlformats.org/package/2006/relationships'}
                    for rel in root.findall('.//r:Relationship', ns):
                        rid = rel.get('Id')
                        target = rel.get('Target')
                        if target and 'media/' in target:
                            media_name = os.path.basename(target)
                            if media_name in image_map:
                                rid_to_media[rid] = image_map[media_name]
    except Exception as e:
        print(f"  Image extraction error: {e}")
    
    current_text = []
    image_index = 0
    image_list = list(image_map.values())
    
    for para in doc.paragraphs:
        drawings = para._element.findall('.//' + qn('w:drawing'))
        picts = para._element.findall('.//' + qn('w:pict'))
        has_image = len(drawings) > 0 or len(picts) > 0
        
        if has_image:
            if current_text:
                text_content = '\n'.join(current_text).strip()
                if text_content:
                    sequence.append({"type": "text", "content": text_content})
                current_text = []
            
            img_path = None
            for drawing in drawings:
                blips = drawing.findall('.//' + qn('a:blip'))
                for blip in blips:
                    embed = blip.get(qn('r:embed'))
                    if embed and embed in rid_to_media:
                        img_path = rid_to_media[embed]
                        break
                if img_path:
                    break
            
            if not img_path and image_index < len(image_list):
                img_path = image_list[image_index]
                image_index += 1
            
            if img_path:
                sequence.append({"type": "image", "path": img_path})
            
            para_text = para.text.strip()
            if para_text:
                current_text.append(para_text)
        else:
            para_text = para.text.strip()
            if para_text:
                current_text.append(para_text)
    
    if current_text:
        text_content = '\n'.join(current_text).strip()
        if text_content:
            sequence.append({"type": "text", "content": text_content})
    
    return sequence


def ensure_english_filenames(directory):
    renamed = {}
    if not os.path.exists(directory):
        return renamed
    
    for filename in os.listdir(directory):
        old_path = os.path.join(directory, filename)
        if os.path.isdir(old_path):
            continue
        
        new_filename = sanitize_filename(filename)
        if new_filename != filename:
            new_path = os.path.join(directory, new_filename)
            counter = 1
            base, ext = os.path.splitext(new_filename)
            while os.path.exists(new_path):
                new_filename = f"{base}_{counter}{ext}"
                new_path = os.path.join(directory, new_filename)
                counter += 1
            
            os.rename(old_path, new_path)
            renamed[old_path] = new_path
            print(f"  Renamed: {filename} -> {new_filename}")
    
    return renamed


if __name__ == "__main__":
    print("=== Filename sanitization test ===")
    test_names = [
        "섹션_1_이미지.png",
        "test_한글_file.docx",
        "normal_file.txt",
        "파일!!!###.jpg"
    ]
    for name in test_names:
        print(f"  {name} -> {sanitize_filename(name)}")
