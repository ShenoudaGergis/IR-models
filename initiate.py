from tkinter import Tk , LabelFrame , Frame , Label , Entry , Button , Scrollbar , Text , Menu , ttk;
from tkinter.filedialog import askopenfile;
from tkinter import messagebox as msg;
from model import BooleanModel , InvertedIndex , VectorSpaceModel;
from tools import minePdf , mineSite;
from contractions import fix;
from inflect import engine;
from nltk.stem import LancasterStemmer, WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer;
from nltk.corpus import stopwords;

def isNnumber(s):
	try:
		float(s)
		return True
	except ValueError:
		pass
	try:
		import unicodedata
		unicodedata.numeric(s)
		return True
	except (TypeError, ValueError):
		pass 
	return False




def wordSym(words) :
	scanned = [];
	flag = "s"; # s for non-digits and d digits
	for word in words :
		wordBuilder = "";
		for index in range(len(word)) :
			if word[index].isalpha() :
				if flag == "s" : 
					wordBuilder += word[index];
					if index == len(word) - 1 : scanned.append(wordBuilder);
				else :
					flag = "s"
					scanned.append(wordBuilder);
					wordBuilder = "";
					wordBuilder = word[index];
					if index == len(word) - 1 : scanned.append(wordBuilder);
			elif word[index].isdigit() :
				if flag == "d" : 
					wordBuilder += word[index];
					if index == len(word) - 1 : scanned.append(wordBuilder);
				else :
					flag = "d"
					scanned.append(wordBuilder);
					wordBuilder = "";
					wordBuilder = word[index];
					if index == len(word) - 1 : scanned.append(wordBuilder);
			elif word[index] == "." :
				if not wordBuilder == "" and wordBuilder.isdigit() : wordBuilder += word[index];
			elif word[index] == "(" or word[index] == ")" :
				scanned.append(wordBuilder);
				wordBuilder = "";
				scanned.append(word[index]);
			else :
				continue

	try :
	 scanned.remove("");
	finally : return scanned


def normalizeWord(words , critical=False) :
	def tokenizer(text):
		#tokenizer = RegexpTokenizer(r'\w+')
		tokenizer = RegexpTokenizer(r'[a-zA-Z0-9\(\).]+')
		return tokenizer.tokenize(text);		
	sw = stopwords.words("english");
	digitConverter = engine();
	words = tokenizer(words);
	words = wordSym(words);
	stemmer = LancasterStemmer();
	lemmatizer = WordNetLemmatizer();
	filtered = [];
	for word in words :
		if not critical :
			if word in ["(",")"] : continue;
			word = word.replace(")","");
			word = word.replace("(","");

		word = fix(word);
		word = word.lower();
		if len(word.split()) != 1 : 
			temp = normalizeWord(word);	
			for splited in temp :
				if splited not in filtered : filtered.append(splited);
			continue;
		if word in sw and critical == True and word in ["and" , "or" , "not"] : pass;
		elif word in sw : continue;  
		if isNnumber(word) :
			temp = digitConverter.number_to_words(word)
			temp = normalizeWord(temp);	
			for splited in temp :
				if splited not in filtered : filtered.append(splited);
			continue;
		word = stemmer.stem(word);
		word = lemmatizer.lemmatize(word , pos="v");

		#if critical : filtered.append(word);continue;
		#if word not in filtered : filtered.append(word);
		filtered.append(word);
	return filtered;


class MainWin(Tk) :
	def __init__(self,title,*args,**kwargs) :
		Tk.__init__(self,*args,**kwargs);
		self.title(title);
		self.docsLim = "-1";
		self.docs = [];
		self.raw  = [];
		self._addMenu();
		self._addUpperTemplate();
		self._addLowerTemplate();

	def _addMenu(self) :
		mainMenu = Menu(self);
		
		fileMenu = Menu(mainMenu , tearoff=0);
		fileMenu.add_command(label="Mine PDF",command=self._pdfMine);
		fileMenu.add_command(label="Site crawling" + " " * 20,command=self._webMine);
		fileMenu.add_separator();
		fileMenu.add_command(label="Exit",command=lambda : exit(0));

		helpMenu = Menu(mainMenu , tearoff=0);
		helpMenu.add_command(label="About" + " " * 20,command=self._about);
		helpMenu.add_command(label="Manual",command=self._manual);

		mainMenu.add_cascade(label="File",menu=fileMenu);
		mainMenu.add_cascade(label="Help",menu=helpMenu);
		self.config(menu=mainMenu);


	def _addUpperTemplate(self) :
		lblFrame = LabelFrame(self,text=" Documents ")
		lblFrame.grid(row=0,column=0,sticky="new",padx=15,pady=15,columnspan=2);

		frame = Frame(lblFrame);
		Label(frame,text="Limit Documents").grid(row=0,column=0,sticky="w",pady=5,padx=10);
		self.combo = ttk.Combobox(frame,values=["None"] + [i for i in range(1,20)] , state="readonly");
		def chooseLim(event) : self.combo.config(state="disabled");self.docsLim=self.combo.get();print(self.docsLim);
		self.combo.bind("<<ComboboxSelected>>", chooseLim);
		self.combo.grid(row=0,column=1,sticky="w")
		self.combo.current(0)
		frame.grid(row=0,column=0,sticky="w")

		frame = Frame(lblFrame)
		xscrollbar = Scrollbar(frame , orient="horizontal")
		xscrollbar.grid(row=1, column=0, sticky="snew")

		yscrollbar = Scrollbar(frame)
		yscrollbar.grid(row=0, column=1, sticky="snew")

		self.text = Text(frame , height=10 , font=("Consolas",12) , wrap="none" , xscrollcommand=xscrollbar.set , yscrollcommand=yscrollbar.set)
		self.text.grid(row=0,column=0,sticky="snew")

		xscrollbar.config(command=self.text.xview)
		yscrollbar.config(command=self.text.yview)		
		frame.grid(row=1,column=0,sticky="snew",padx=10,pady=(5,0))
	
		self.fileChoose = Label(lblFrame,text="Import from a text file",font=("consolas",10),fg="blue",cursor="hand2");
		self.fileChoose.grid(row=2,column=0,sticky="w",padx=10)
		self.fileChoose.bind("<Button-1>",lambda event : self._importText());

		rightFrame = Frame(lblFrame);
		Button(rightFrame,text="Add as a Document",relief="groove",command=self._addDoc).grid(row=0,column=0,ipady=4,padx=(5,15),pady=2,sticky="we")
		Button(rightFrame,text="Remove all Documents",relief="groove",command=self._removeDocs).grid(row=1,column=0,ipady=4,padx=(5,15),pady=2,sticky="we")
		Button(rightFrame,text="Past a Document",relief="groove",command=self._pastDoc).grid(row=2,column=0,ipady=4,padx=(5,15),pady=2,sticky="we")
		Button(rightFrame,text="Show Documents",relief="groove",command=self._showDocs).grid(row=3,column=0,ipady=4,padx=(5,15),pady=2,sticky="we");

		rightFrame.grid(row=1,column=1)

		frame2 = Frame(lblFrame);
		Label(frame2,text="Search Engine Mode").grid(row=0,column=0,sticky="w",pady=5,padx=10);
		self.combo2 = ttk.Combobox(frame2,values=["Boolean Retrival Model","Inverted Index Model","Vector Space Model"] , state="readonly");
		self.combo2.grid(row=0,column=1,sticky="we",columnspan=2,padx=(10,10))
		self.combo2.current(0)
		frame2.grid(row=3,column=0,sticky="snew",pady=15);
		frame2.columnconfigure(2,weight=1)

		frame.columnconfigure(0,weight=1);
		self.columnconfigure(0,weight=1);
		self.rowconfigure(0,weight=1);
		frame.rowconfigure(0,weight=1);
		lblFrame.rowconfigure(0,weight=4);
		lblFrame.columnconfigure(0,weight=1);

	def _addLowerTemplate(self) :
		self.searchEntry = Entry(self , font=("consolas",12));
		self.searchEntry.grid(row=1,column=0,ipady=2,padx=15,pady=10,sticky="wen")
		Button(self,text="Search",relief="groove",command=self._search).grid(row=1,column=1,ipadx=15,ipady=1,padx=(0,15),pady=(10,30));

	def _addDoc(self) :
		if self.docsLim == "-1" :
			msg.showerror("Error","You should set the limited number of documents first");
			return;
		else :
			if self.docsLim == "None" : 
				doc = self.text.get("0.1" , "end")
				raw = doc;
				doc = doc.replace("\n"," ");
				doc = normalizeWord(doc);       #
				if len(doc) == 0 : print("empty");return;
				self.docs.append(doc);
				self.raw.append(raw);
				print(self.docs)
			else : #must be then from 1 to 19
				if int(self.docsLim) == len(self.docs) : msg.showerror("Error","Maximum number of documents reached"); 
				else : 
					doc = self.text.get("0.1" , "end")
					raw = doc;
					doc = doc.replace("\n"," ");
					doc = normalizeWord(doc);
					#self.docs.append(filterFromSW(doc));
					if len(doc) == 0 : print("empty");return;
					self.docs.append(doc);
					self.raw.append(raw);
					print(self.docs)
				
	def _removeDocs(self) :
		self.docs = [];
		self.raw  = [];
		self.docsLim = "-1";
		self.combo.configure(state="readonly");
		self.combo.current(0);

	def _pastDoc(self) :
		from clipboard import paste
		content = paste();
		if not content.replace(" ","").replace("\n","") == "" : 
			self.text.delete("0.1","end");
			self.text.insert("0.1" , content)

	def _showDocs(self) :
		out = "";
		if len(self.docs) == 0 : out = "No documents added so far";
		else :
			for i in range(len(self.raw)) :
				out += "-Doc <" + str(i+1) + "> :\n" + self.raw[i] + "\n\n"; 
		self.popup("jesus christ" , out);

	def _pdfMine(self) :
		def isPdfFile(filePath) :
			if filePath.split(".")[-1] == "pdf" : return True;
			return False;
		pdfFilePath = askopenfile();
		try :
			if isPdfFile(pdfFilePath.name) :
		
				content = minePdf(pdfFilePath.name);
				if content != False :
					self.text.delete("0.1","end");
					self.text.insert("0.1",content);
		except : print("passed");

	def _webMine(self) :
		def getURL(entry=Entry()) :
			given = entry.get();
			if given.replace(" ","") == "" : return;
			content = mineSite(given);
			if content == False : msg.showerror("Error","Invalid URL specified or No Internet connection Found");
			else :
				self.text.delete("0.1","end");
				self.text.insert("0.1",content);
				
		pop = Tk();
		pop.title("jesus christ")
		pop.columnconfigure(0,weight=1);
		Label(pop,text="please fill below a valid url").grid(row=0,column=0,sticky="w",padx=10,pady=5)
		entry = Entry(pop,font=("Consolas",11));
		entry.grid(row=1,column=0,sticky="we",padx=10,pady=(5,20),ipadx=2,ipady=2);
		Button(pop,text="retrieve",relief="groove",command=lambda : getURL(entry)).grid(row=1,column=1,padx=5,pady=(5,20),ipadx=3,ipady=1);
		pop.minsize(400,100)
		pop.maxsize(800,100)
		pop.mainloop();

	def _manual(self) :
		content = "";
		try :
			with open("README.txt","r") as file :
				content = "".join(file.readlines());
		except : pass;
		finally :
			self.popup("jesus christ" , content);

	def _about(self) :
		pop = Tk();
		pop.title("jesus christ")
		pop.resizable(False , False)
		Label(pop,text="Team IR project 1st term 2018 - 2019\n\n").grid(row=0,column=0,padx=(10,20),pady=(10,100))
		pop.mainloop();

	def _importText(self) :
		def isTextFile(filePath) :
			if filePath.split(".")[-1] == "txt" : return True;
			return False;
		try :
			with askopenfile() as file :
				if isTextFile(file.name) : 
					content = "";
					for line in file.readlines() :
						if not line.replace(" ","").replace("\n","") == "" :
							content += line;
					if not content == "" :  
						self.text.delete("0.1","end");
						self.text.insert("0.1",content);
		except : return;

	def _search(self) :
		if self.docsLim != "-1" and len(self.docs) != 0 :
			mode  = self.combo2.get();
			query = self.searchEntry.get();
			if query.replace(" ","") == "" : return; 
			if mode == "Boolean Retrival Model" :
				model1 = BooleanModel(self.docs , self.raw , normalizeWord(query , True));
				result = model1.getSol()
				if result == False : msg.showerror("Error","Syntax error found in the query");
				else :
					#print(result);
					self.popup("jesus christ" , model1.foramtter(result))

			elif mode == "Inverted Index Model" : 
				model2 = InvertedIndex(self.docs , self.raw , normalizeWord(query));
				result = model2.getSol();
				self.popup("jesus christ" , model2.formatter(result));
				
			elif mode == "Vector Space Model" :
				model3 = VectorSpaceModel(self.docs , self.raw , normalizeWord(query));
				result = model3.getSol();
				self.popup("jesus christ" , model3.formatter(result));

		else :
			msg.showerror("Error","Please add documents first");

	@staticmethod
	def popup(title , content) :
		root = Tk();
		root.title(title)
		frame = Frame(root)
		xscrollbar = Scrollbar(frame , orient="horizontal")
		xscrollbar.grid(row=1, column=0, sticky="snew")

		yscrollbar = Scrollbar(frame)
		yscrollbar.grid(row=0, column=1, sticky="snew")

		text = Text(frame , height=10 , font=("Consolas",12) , wrap="none" , xscrollcommand=xscrollbar.set , yscrollcommand=yscrollbar.set)
		text.grid(row=0,column=0,sticky="snew")

		xscrollbar.config(command=text.xview)
		yscrollbar.config(command=text.yview)		
		frame.grid(row=0,column=0,sticky="snew",padx=10,pady=(5,0))

		text.insert("0.1" , content);
		text.configure(state="disabled");

		root.columnconfigure(0,weight=1);
		root.rowconfigure(0,weight=1);
		frame.columnconfigure(0,weight=1);
		frame.rowconfigure(0,weight=1);


	def run(self) :
		self.mainloop();


MainWin("jesus christ").run();
