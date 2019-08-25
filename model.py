#from nltk.tokenize import RegexpTokenizer;
from math import log10 ,sqrt , degrees;

class BooleanModel :
	def __init__(self , docs , raw , query) :
		self.docs  = docs;
		self.raw   = raw; 
		self.query = query;
		self.terms = BooleanModel.buildTerms(self.docs);
		self.buildIncidenceMatrix();

	@staticmethod
	def buildTerms(docs) :
		terms = [];
		for doc in docs :
			for term in doc :
				if term not in terms : terms.append(term);
		return terms;

	def buildIncidenceMatrix(self) :
		self.matrix = [];
		for term in self.terms :
			self.matrix.append([0 for i in range(len(self.docs))]);
			for i in range(len(self.docs)) :
				if term in self.docs[i] : self.matrix[-1][i] = 1;
		#return self.matrix

	def parseQuery(self) :
		def tokenizer():
			tokenizer = RegexpTokenizer(r'\w+')
			return tokenizer.tokenize(self.query);

		def binary(prefix , body) :
			bits = prefix;
			for bit in body :
				bits += str(bit);
			return bits;

		#query = tokenizer();
		#query = [word.lower() for word in query];
		bits = "";
		for word in self.query :
			print(self.query)
			if word == "and" : bits += " & ";
			elif word == "or" : bits += " | ";
			elif word == "not" : bits += " 0b" + "1" * len(self.docs) + " - ";
			elif word in ["(",")"] : bits += " " + word + " ";
			else :
				try :
					index = self.terms.index(word);
				except :
					bits += "0b" + "0" * len(self.docs) + " ";
				else :
					bits += binary("0b" , self.matrix[index]) + " ";
		print(bits)
		return bits;


	def solve(self) :
		bits = self.parseQuery();
		solution = "";
		try :
			solution = bin(eval(bits))[2:].zfill(len(self.docs));
		except : 
			return False;
		else :
			return solution;


	def getSol(self) :
		sol = self.solve();
		if sol == False : return False;
		index = 0;
		selectedDocs = [];
		for index,bit in zip(range(len(self.docs)) , sol) :
			if bit == "1" :
				selectedDocs.append(index);
		return [(" ".join(self.query)) , (self.terms) , (self.matrix) , [self.raw[i].replace("\n","") for i in range(len(self.docs)) if i in selectedDocs]];


	@staticmethod
	def foramtter(data) :
		print(data)
		out = "";
		out += "+Query\n" + "-" * 8 + "\n" + data[0] + "\n\n";
		terms = data[1];
		matrix = data[2];
		matchedDocs = data[3];
		out += "+Incidence Matrix\n" + "-" * 20 + "\n"
		for i in range(len(matrix[-1])) :
			out += "Doc<"+ str((i+1)) + ">\t\t";
		out += "\n";
		for vector,term in zip(matrix , terms) :
			for bit in vector :
				out += "  " + str(bit) + " " * 13;
			out += "  " + str(term) + "\n";
		out += "\n\n+Matched Documents\n" + "-" * 20 + "\n";
		for i in range(len(matchedDocs)) :
			out += str(i+1) + " ) " + matchedDocs[i] + "\n\n";
		
		return out;


class InvertedIndex :
	def __init__(self , docs , raw , query) :
		self.docs = docs;
		self.raw  = raw;
		self.query = query;
		self.terms = BooleanModel.buildTerms(self.docs);
		self.postingDict = {};
		self.buildPostingDict();
		self.parseQuery();

	def buildPostingDict(self) :
		for term in self.terms :
			self.postingDict[term] = [];
			for i in range(len(self.docs)) :
				if term in self.docs[i] : self.postingDict[term].append(i);
			#self.postingDict[term] = tuple(self.postingDict[term]);
		self.postingDict = dict(sorted(self.postingDict.items()));
		print(self.postingDict)

	def parseQuery(self) :
		querySet = [];
		self.queryPostingDict = {};
		for token in self.query :
			try :
				querySet.append(self.postingDict[token]);
			except KeyError :
				querySet.append([]);
			else :
				self.queryPostingDict[token] = self.postingDict[token];
		#[[0],[0,1],[1],[1,0],[]];
		self.exactSet = [];
		self.otherSet = [];
		if len(querySet) == 0 : return;
		self.exactSet = list(set(querySet[0]).intersection(*querySet[1:]));
		self.otherSet = list(set(querySet[0]).union(*querySet[1:]));
		print(self.otherSet)
		print(self.exactSet)
		#for index in self.otherSet : 
			#if index in self.exactSet : self.otherSet.remove(index);
		self.otherSet = list(set(self.otherSet).difference(set(self.exactSet)))
		print(self.otherSet)

	def getSol(self) :
		return [" ".join(self.query) , self.docs , self.postingDict , self.queryPostingDict , self.exactSet , self.otherSet , self.raw];

	@staticmethod
	def formatter(data) :
		def formatWord(sent) :
			for i in range(20 - len(sent)) :
				sent += " ";
			return sent;
		out = "";
		out += "+Query\n" + "-" * 8 + "\n" + data[0] + "\n\n";
		out += "+Documents Terms\n" + "-" * 20 + "\n";
		for i in range(len(data[1])) :
			temp = " , ".join(data[1][i]);
			out += "-Doc <" + str(i+1) + "> : ===> { " + temp + " }\n";
		out += "\n\n+Documents Posting Dict\n" + "-" * 28 + "\n";
		for item in data[2] :
			out += formatWord(str(item)) + "  =====>  " + " , ".join([str(i) for i in data[2][item]]) + "\n";
		out += "\n\n+Query Posting Dict\n" + "-" * 25 + "\n";
		for item in data[3] :
			out += formatWord(str(item)) + "  =====>  " + " , ".join(str(i) for i in data[3][item]) + "\n";

		out += "\n\n+Matched Documents\n" + "-" * 25 + "\n\n";
		out += "# exact matched\n" + "~" * 20 + "\n";
		if len(data[4]) == 0 : out += "Oops No matched found\n\n"
		else :
			for index in data[4] :
				out += "-Doc <" + str(index) + ">\n" + data[-1][index] + "\n\n";
		out += "# other matched\n" + "~" * 20 + "\n";
		for index in data[5] :
			out += "-Doc <" + str(index) + ">\n" + data[-1][index] + "\n\n";

		return out;

class VectorSpaceModel :
	def __init__(self , docs , raw , query) :
		self.docs = docs;
		self.raw  = raw;
		self.query = query;
		self.terms = BooleanModel.buildTerms(self.docs);
		self.docs2vector()
		self.query2vector();
		#print(self.queryVector);
		#print(self.docsVectors);
		#print("\n",self.terms)


	def df(self , term) :
		df = 0;
		for doc in self.docs :
			if term in doc : df += 1;
		return df;

	@staticmethod
	def dotProduct(v1 , v2) :
		return sum([bit1*bit2 for bit1,bit2 in zip(v1,v2)])

	@staticmethod
	def vectorLen(v) :
		return float(str(sqrt(sum([bit**2 for bit in v])))[:6]);

	@staticmethod
	def cosineSimilarity(d , q) :
		result = 0.0000;
		try :
			result = float(str(VectorSpaceModel.dotProduct(d , q) / (VectorSpaceModel.vectorLen(d) * VectorSpaceModel.vectorLen(q)))[:6]);
		except : 
			if result == 0.0 : return 0.0000
		else :
			return result;

	def docs2vector(self) :
		self.docsVectors = [];
		for doc in self.docs :
			self.docsVectors.append([]);
			for term in self.terms :
				if term in doc :
					print(doc.count(term));
					self.docsVectors[-1].append(float(str(doc.count(term) * log10((len(self.docs) / self.df(term))))[:6]));
				else :
					self.docsVectors[-1].append(0.0000);


	def query2vector(self) :
		self.queryVector = [];
		for term in self.terms :
			if term in self.query :
				self.queryVector.append(float(str(self.query.count(term) * log10(len(self.docs) / self.df(term)))[:6]));
			else :
				self.queryVector.append(0.0000);


	def rankHits(self) :
		results = [];
		for i in range(len(self.docsVectors)) :
			rad = self.cosineSimilarity(self.docsVectors[i] , self.queryVector)
			results.append((rad , round(degrees(rad),2) , i));
		results.sort(key=lambda tup : tup[0] , reverse = True);
		return results


	def getSol(self) :
		return [" ".join(self.query) , self.terms , self.docsVectors , self.queryVector , [(i[0],i[1],self.raw[i[2]]) for i in self.rankHits()]]

	@staticmethod
	def formatter(data) :
		def formatNumber(num) :
			for i in range(6 - len(num)) :
				num += "0";
			return num;
		out = "";
		out += "+Query\n" + "-" * 8 + "\n" + data[0] + "\n\n";
		out += "+TF-IDF Matrix" + "\n" + "-" * 17 + "\n";
		for i in range(len(data[2])) :
			out += "Doc<" + str((i+1)) + ">\t\t";
		out += "Query\n\n";
		for i in range(len(data[1])) :
			for j in range(len(data[2])) :
				out += formatNumber(str(data[2][j][i])) + " " * 10
			out += formatNumber(str(data[3][i])) + " " * 10;
			out += data[1][i] + "\n";
		out += "\n\n+Ranked Hits From Higher to Lower\n" + "-" * 36 + "\n\n";
		i = 1;
		for hit in data[-1] :
			out += str(i) + " ) Similarity in rad : " + formatNumber(str(hit[0])) + " , Cosine Similarity in deg : " + str(hit[1]) + "\n";
			out += "-doc : " + hit[-1] + "\n";
			i += 1;
		return out;

#print(VectorSpaceModel([["jesus","christ","love"],["mariam","el","adra","save"],["philopateer","jesus","hero"]] , "" , ["mariam","el","adra","save"]).rankHits());
#print(VectorSpaceModel("" , "" , "").cosineSimilarity([0.12,1.23,0.56],[1.01,0.66,0.02]));
#i = InvertedIndex([["jesus","christ","love"],["mariam","el","adra","save"],["philopateer","jesus","hero"]] , "" , ["mariam","el","adra","jesus"])
#print(i.exactSet , i.otherSet)
a = {"a":[2,3,6],"b":[9,0,2],"c":[1,0,3]};
for item in a :
	print(item);



#if "__name__" == "__main__" :
	#b = BooleanModel([["jesus","christ","loves","we"],["we","adore","abouna","fanouse"],["abouna","Falta2os","is","here"],["loves","jesus","philopateer"],["mariam","el","adra","we","love"]] , "" , "marina");
	#print(b.parseQuery())
	#print(b.solve());
	#print(b.getSol());
	#print(bin(eval("0b111 - 0b110"))[2:].zfill(3));
	#BooleanModel("" , "" , "").foramtter(['jesus OR Mariam', ['mariam', 'el', 'adra', 'mother', 'humantiy', 'jesus', 'christ', 'god', 'help', 'us', 'every', 'saves'], [[1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 0, 0], [1, 0, 0], [0, 1, 1], [0, 1, 1], [0, 1, 0], [0, 1, 0], [0, 1, 1], [0, 1, 0], [0, 0, 1]], [['mariam el adra is the mother of humantiy'], ['jesus christ is god and help us everywhere'], ['jesus christ and mariam el adra saves us']]]);










