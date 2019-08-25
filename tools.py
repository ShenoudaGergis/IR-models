def minePdf(filePath) :
	from PyPDF2 import PdfFileReader;
	try :
		file = open(filePath ,"rb");
	except :
		return False;
	else :
		pdfFile = PdfFileReader(file);
		pdfFilePagesCount = pdfFile.numPages;
		page = 0;
		text = "";
		try :
			while page < pdfFilePagesCount :
				text += pdfFile.getPage(page).extractText();
				page += 1;
		except : pass;
		return text;

#print(minePdf("C:/Users/Kirollos Nasr/Desktop/jesus christ before mid.pdf"));



def mineSite(url) :
	from html2text import html2text;
	import requests
	try :
		r = requests.get(url)
		content = html2text(r.text);
		return content
	except :
		return False;

#print(mineSite("https://www.facebook.com/"))