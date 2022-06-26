from PIL import Image
import pyocr
import os
import PySimpleGUI as sg
import json
import webbrowser
from urllib import parse

OCR_ENGENE_NAME = 'tesseract'
FILENAME_CONFIG_LANG = 'lang.json'
BASEURL_DEEPL = 'https://www.deepl.com/translator'

FONT_SETTING = {'font': ('Arial',22)}

sg.theme('DarkAmber')


with open(FILENAME_CONFIG_LANG, mode='r', encoding='utf-8') as f:
    lang_dict = json.load(f)

# Define the class for pysimplegui
class Window:
    def __init__(self, title:str, layout:list=None, **kwargs):
        """Generate a window with a title and a layout for pysimplegui.

        Parameters
        ----------
        title : str
            Title of the window.
        layout : list, optional
            Layout of the window., by default None
        """
        self.title = title
        self.layout = layout
        # ウィンドウを作成する
        self.window = sg.Window(title=self.title, layout=self.layout, element_justification='center', resizable=True, **kwargs)
    
    def __del__(self):
        """Destructor for the window.
        """
        self.close()
    
    def close(self):
        """Close the window.
        """
        self.window.close()
    
    def read(self)->None:
        """Read the window and get the event and the values.

        You can get the event and the values by this method.

        You can refer them by `self.event` and `self.values`.
        """
        self.event, self.values = self.window.read()
    
    # You shold override this method
    def update(self)->None:
        """Update the window.

        You should override this method.

        Examples
        --------
        >>> def update(self):
        ...     while True:
        ...         self.read()
        ...         if self.event is None:
        ...             break

        """
        while True:
            self.read()
            if self.event is None:
                break


class OCR:
    def __init__(self) -> None:
        self.engine = self._get_engine()
    
    def get_text(self, file_path:str, lang='eng')->str:
        """Get text from an image.

        Parameters
        ----------
        file_path : str
            Path of the image file.
        lang : str, optional
            Language of the text., by default 'eng'

        Returns
        -------
        str
            Text from the image.
        """
        image = self._get_image(file_path)
        return self.engine.image_to_string(image, lang=lang)

    # OCRエンジンを取得
    def _get_engine(self):
        """Get an OCR engine.
        """
        engines = pyocr.get_available_tools()
        for _engine in engines:
            if OCR_ENGENE_NAME in _engine.__name__:
                return _engine
        else:
            raise ModuleNotFoundError(f'No module named {OCR_ENGENE_NAME}')

    def _get_image(self, file_path:str)->Image.Image:
        """Get an image from a file.

        Parameters
        ----------
        file_path : str
            Path of the image file.

        Returns
        -------
        Image.Image
            Image object.
        
        Raises
        ------
        FileNotFoundError
            If the file is not found.
        """
        if os.path.isfile(file_path):
            return Image.open(file_path)
        else:
            raise FileNotFoundError(f'No such file: {file_path}')

class MainWindow(Window):
    def __init__(self):
        # setup for OCR
        try:
            self.ocr = OCR()
        except ModuleNotFoundError:
            sg.PopupError('No OCR engine found.')
            exit(1)

        super().__init__(title='OCR', layout=[
            [sg.InputText(size=(30, 1), key='input_file_path', **FONT_SETTING), sg.FileBrowse(file_types=(('Image Files', '*.png'), ('All Files', '*.*')), **FONT_SETTING)],
            [sg.Text()],
            [sg.Text('Language', **FONT_SETTING), sg.Combo(
                list(lang_dict.keys()),
                default_value=list(lang_dict.keys())[0],
                key='language', **FONT_SETTING
            )],
            [sg.Text()],
            [sg.Submit('Run', **FONT_SETTING), sg.CloseButton('Close', **FONT_SETTING)],
        ])

    def update(self):
        while True:
            self.read()
            if self.event is None or self.event == 'Close':
                break
            elif self.event == 'Run':
                # 画像の文字を読み込む
                results_ocr = self.ocr.get_text(file_path=self.values['input_file_path'], lang=lang_dict[self.values['language']]['code_tesseract'])
                result_window = ResultWindow(text=results_ocr, lang=self.values['language'])
                result_window.update()
                del result_window
                

class ResultWindow(Window):
    def __init__(self, text:str, lang:str):
        """Result window.

        Parameters
        ----------
        text : str
            Text from the image.
        
        lang : str
            Language of the text.
        """
        self.text = text
        self.lang = lang
        super().__init__(title='OCR', layout=[
            [sg.Text('Result', **FONT_SETTING)],
            [sg.Multiline(text, size=(30, 10), key='result', **FONT_SETTING)],
            [sg.Checkbox('Remove line breaks', default=True, key='flag_remove_line_breaks', **FONT_SETTING)],
            [sg.Submit('Translate', **FONT_SETTING), sg.CloseButton('Close', **FONT_SETTING)],
        ])
        # Windowsの作成から、window.read() までの間にWindow上のエレメントにアクセスする場合は、finalize=Trueを指定する必要があります。
        # https://naotoshisami.com/2022/02/pysimplegui-window-element-init/

        if self.lang == '日本語':
            self.lang_translate_to = 'English'
        else:
            self.lang_translate_to = '日本語'

    
    def update(self):
        while True:
            self.read()
            if self.event is None or self.event == 'Close':
                break
            elif self.event == 'Translate':
                if self.values['flag_remove_line_breaks']:
                    text = self.text.replace('\n', ' ')
                else:
                    text = self.text
                text_uri_escaped = parse.quote(text)
                # 翻訳する
                url_translate = f'{BASEURL_DEEPL}#{lang_dict[self.lang]["code_deepl"]}/{lang_dict[self.lang_translate_to]["code_deepl"]}/{text_uri_escaped}'
                webbrowser.open(url_translate)
                

if __name__ == '__main__':
    main_window = MainWindow()
    main_window.update()
    del main_window
    

