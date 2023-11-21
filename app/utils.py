import fitz  # PyMuPDF
import os
from django.conf import settings

def convert_pdf_to_img(pdf_file):
    full_pdf_path = pdf_file.path
    output_dir = os.path.join('uploads/pdf_images')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # 이미지 저장 디렉토리가 없다면 생성합니다.

    # PDF 문서를 엽니다.
    try:
        doc = fitz.open(full_pdf_path)
        page = doc[0]  
        pix = page.get_pixmap()  # 페이지를 이미지 픽셀맵으로 변환합니다.

        # 이미지 파일의 이름을 설정합니다. 예를 들어 'some_document.pdf'는 'some_document.png'가 됩니다.
        img_filename = os.path.splitext(pdf_file.name)[0] + '.png'
        full_img_path = os.path.join(img_filename)  # 이미지의 전체 경로를 설정합니다.
        
        # 이미지 파일을 저장합니다.
        print(f"Attempting to save image to: {full_img_path}")
        try:
            pix.save(full_img_path)
            print(f"Image successfully saved to: {full_img_path}")
        except Exception as e:
            print(f"Failed to save image: {e}")

        
        # 이미지 파일의 상대 경로를 반환합니다. 이를 통해 HTML 템플릿에서 사용할 수 있습니다.
        relative_img_path = os.path.join(img_filename)
        return relative_img_path
    except Exception as e:
        print(f"Error converting PDF to image: {e}")
        return None
    finally:
        if doc:
            doc.close()  
            
            
def convert_pdf_to_img_all(pdf_file):
    full_pdf_path = pdf_file.path
    output_dir = os.path.join('uploads/pdf_images')  # MEDIA_ROOT를 사용하여 경로 설정
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # 이미지 저장 디렉토리가 없다면 생성합니다.

    image_paths = []  # 변환된 이미지의 경로를 저장할 리스트

    try:
        doc = fitz.open(full_pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap()

            img_filename = f"{os.path.splitext(pdf_file.name)[0]}_{page_num}.png"
            full_img_path = os.path.join(img_filename)

            print(f"Attempting to save image to: {full_img_path}")
            try:
                pix.save(full_img_path)
                print(f"Image successfully saved to: {full_img_path}")
                image_paths.append(os.path.join(img_filename))  # 상대 경로를 리스트에 추가
            except Exception as e:
                print(f"Failed to save image: {e}")
    except Exception as e:
        print(f"Error converting PDF to image: {e}")
    finally:
        if 'doc' in locals():
            doc.close()

    return image_paths