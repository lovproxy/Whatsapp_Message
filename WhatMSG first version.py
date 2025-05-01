import webbrowser
import pyautogui
import time
import sys
import fitz
import PyPDF2
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
import pdfplumber
from PIL import Image
from pdf2image import convert_from_path 
import pytesseract 
import os
import os
from PyPDF2 import PdfFileReader
import wx
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
class Window(wx.Frame):
          result=[]
          def __init__(self, parent, title):
                    wx.Frame.__init__(self, parent, title = title, size = (1000,1000))
                    wx.StaticText(self, wx.ID_ANY, "Введите номера телефонов через запятую без +7 в поле ниже:",size=(500,50))
                    yea = wx.Button(self,label='Отправить', size=(100,50),pos=(880,0))
                    self.control = wx.TextCtrl(self, style = wx.TE_MULTILINE,size=(1000,100),pos=(0,60))
                    yea.Bind(wx.EVT_BUTTON,self.Onyea)
                    self.btn = wx.Button(self, label="Прикрепить файл",size=(150,50),pos=(730,0))
                    self.btn.Bind(wx.EVT_BUTTON, self.OnclickMe)
                    wx.StaticText(self, wx.ID_ANY, "Введите сообщение в поле ниже:",size=(500,50),pos = (0,160))
                    self.control2 = wx.TextCtrl(self, style = wx.TE_MULTILINE,size=(1000,200),pos=(0,210))
          def Onyea(self,event):
                    number = ''
                    msg = self.control2.GetValue()
                    if len(self.control.GetValue())!=0:
                              number = self.control.GetValue()
                              number = number.split(',')
                    elif len(result)!=0:
                              for x in range(len(result)):
                                        number+=result[x]+','
                    else:
                              wx.MessageBox('Введите номера телефонов в первое окно или прикрепите PDF файл!', 'Dialog', wx.OK | wx.ICON_ERROR)
                    if len(number)!=0:
                              o = 0
                              for i in range(len(number)):
                                        if number[i]==',':
                                                  q = number[o:i]
                                                  o = i+1
                                                  web = webbrowser.open_new_tab(f'https://web.whatsapp.com/send?phone=+7{q}&text={msg}')
                                                  time.sleep(10)
                                                  pyautogui.press('enter')
                                                  pyautogui.press('enter')
                                                  os.system("taskkill /im msedge.exe /f")
          def OnclickMe(self,event):
                    global result
                    def text_extraction(element):
                              line_text = element.get_text()
                              line_formats = []
                              for text_line in element:
                                        if isinstance(text_line, LTTextContainer):
                                                  for character in text_line:
                                                            if isinstance(character, LTChar):
                                                                      line_formats.append(character.fontname)
                                                                      line_formats.append(character.size)
                              format_per_line = list(set(line_formats))
                              return (line_text, format_per_line)
                    def crop_image(element, pageObj):
                              [image_left, image_top, image_right, image_bottom] = [element.x0,element.y0,element.x1,element.y1]
                              pageObj.mediabox.lower_left = (image_left, image_bottom)
                              pageObj.mediabox.upper_right = (image_right, image_top)
                              cropped_pdf_writer = PyPDF2.PdfWriter()
                              cropped_pdf_writer.add_page(pageObj)
                              with open('cropped_image.pdf', 'wb') as cropped_pdf_file:
                                        cropped_pdf_writer.write(cropped_pdf_file)
                    def convert_to_images(input_file,):
                              images = convert_from_path(input_file)
                              image = images[0]
                              output_file = "PDF_image.png"
                              image.save(output_file, "PNG")
                    def image_to_text(image_path):
                              img = Image.open(image_path)
                              text = pytesseract.image_to_string(img)
                              return text
                    def extract_table(pdf_path, page_num, table_num):
                              pdf = pdfplumber.open(pdf_path)
                              table_page = pdf.pages[page_num]
                              table = table_page.extract_tables()[table_num]
                              return table
                    def table_converter(table):
                              table_string = ''
                              for row_num in range(len(table)):
                                        row = table[row_num]
                                        cleaned_row = [item.replace('\n', ' ') if item is not None and '\n' in item else 'None' if item is None else item for item in row]
                                        table_string+=('|'+'|'.join(cleaned_row)+'|'+'\n')
                                        table_string = table_string[:-1]
                              return table_string
                    with wx.FileDialog(self, "Open pdf file", wildcard="pdf files (*.pdf)|*.pdf",
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
                              if fileDialog.ShowModal() == wx.ID_CANCEL:
                                        return
                              pathname = fileDialog.GetPath()
                              try:
                                        text_per_page = {}
                                        pdf_path = pathname
                                        f = open(pathname,'rb')
                                        pdfReaded = PyPDF2.PdfReader(f)
                                        for pagenum, page in enumerate(extract_pages(pathname)):    
                                                            pageObj = pdfReaded.pages[pagenum]
                                                            page_text = []
                                                            line_format = []
                                                            text_from_images = []
                                                            text_from_tables = []
                                                            page_content = []
                                                            table_num = 0
                                                            first_element= True
                                                            table_extraction_flag= False
                                                            pdf = pdfplumber.open(pdf_path)
                                                            page_tables = pdf.pages[pagenum]
                                                            tables = page_tables.find_tables()
                                                            page_elements = [(element.y1, element) for element in page._objs]
                                                            page_elements.sort(key=lambda a: a[0], reverse=True)
                                                            for i,component in enumerate(page_elements):
                                                                      pos= component[0]
                                                                      element = component[1]
                                                                      if isinstance(element, LTTextContainer):
                                                                                if table_extraction_flag == False:
                                                                                          (line_text, format_per_line) = text_extraction(element)
                                                                                          page_text.append(line_text)
                                                                                          line_format.append(format_per_line)
                                                                                          page_content.append(line_text)
                                                                                else:
                                                                                          pass
                                                                      if isinstance(element, LTFigure):
                                                                                                    crop_image(element, pageObj)
                                                                                                    convert_to_images('cropped_image.pdf')
                                                                                                    image_text = image_to_text('PDF_image.png')
                                                                                                    text_from_images.append(image_text)
                                                                                                    page_content.append(image_text)
                                                                                                    page_text.append('image')
                                                                                                    line_format.append('image')
                                                                      if isinstance(element, LTRect):
                                                                                if first_element == True and (table_num+1) <= len(tables):
                                                                                          lower_side = page.bbox[3] - tables[table_num].bbox[3]
                                                                                          upper_side = element.y1
                                                                                          table = extract_table(pdf_path, pagenum, table_num)
                                                                                          table_string = table_converter(table)
                                                                                          text_from_tables.append(table_string)
                                                                                          page_content.append(table_string)
                                                                                          table_extraction_flag = True
                                                                                          first_element = False
                                                                                          page_text.append('table')
                                                                                          line_format.append('table')
                                                                                if element.y0 >= lower_side and element.y1 <= upper_side:
                                                                                          pass
                                                                                elif not isinstance(page_elements[i+1][1], LTRect):
                                                                                                    table_extraction_flag = False
                                                                                                    first_element = True
                                                                                                    table_num+=1
                                                                      dctkey = 'Page_'+str(pagenum)
                                                                      text_per_page[dctkey]= [page_text, line_format, text_from_images,text_from_tables, page_content]
                                        f.close()
                                        try:
                                                  os.remove('cropped_image.pdf')
                                        except FileNotFoundError:
                                                  pass
                                        try:
                                                  os.remove('PDF_image.png')
                                        except FileNotFoundError:
                                                  pass
                                        result = ''.join(text_per_page['Page_0'][4])
                                        o = 0
                                        b = []
                                        for i in range(len(result)):
                                                  if result[i]==' ':
                                                            p=i
                                                            b.append(result[o:p])
                                                            o=p+1
                                        result = []
                                        for x in range(len(b)):
                                                  if '+7' in b[x]:
                                                            b[x]=b[x].replace('\n','')
                                                            result.append(b[x][2:])
                              finally:
                                        wx.MessageBox('Ваш файл успешно прикреплён!Введите ваше сообщение:', 'Dialog', wx.OK | wx.ICON_INFORMATION)
                                        wx.StaticText(self, wx.ID_ANY, "Текст,который удалось получить из PDF:",size=(500,50),pos = (0,410))
                                        pol= wx.TextCtrl(self, style = wx.TE_MULTILINE,size=(1000,200),pos=(0,460))
                                        result2 = ''
                                        for x in range(len(result)):
                                                  result2+=result[x]+','
                                        pol.SetValue(result2[:len(result2)-1])
app = wx.App()
wnd = Window(None, "Whatmsg")
wnd.Show(True)
app.MainLoop()
