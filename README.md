# Alpha Morpho: A Morphological Concordancer

Introduction：Alpha Morpho is based on MorphoLex expanded, a morphological database for 390,000 English words. Alpha Morpho can search the affix of word, all affixes in a text, and calculate morphological complexity of a text.

## Function one: searching affix of a word
1.	If you input a word, you can get its part of speech, derivational prefix, root, derivational suffix, inflectional suffix and type of inflection (e.g. past tense). If the word has many part of speech, all related affix will be listed out. For example, interested can be either an adjective or the past tense of word interest.
2.	Acquire all words with the same root.

## Function two: searching all affixes of a text
1.	Choose a file, and get the coverage (words found in MorphoLex expanded / all words).
2.	Acquire frequency of and words of prefixes, roots, suffixes occurred in the text. 

## Function three: calculating morphological complexity (Sánchez-Gutiérrez, 2018)
Six predicators：
(1) Morphological family size：all types containing the morpheme
	e.g. {attendance, pleasance, pleasure, appearance}    
		 -ance {attendance,pleasance,appearance} family size = 3   
		 plea- {pleasance, pleasure} family size = 2
	
(2) summed token frequency：all tokens containing the morpheme
	e.g.  -ance attendance, appearance, pleasance   sum frequency
	
(3)(4) affix productivity, P & P*
	P = hapax containing the morpheme / summed token frequency of the 
	P* = hapax containing the morpheme / all hapaxes
	
(5) PFMF: the order of morpheme in word family (0-1,most frequent = 100%)
	PFMF = (order-1) / Morphological family size -1
	
(6) affix length: length of affix（do not distinguish allomoph）
	*-ion, -tion, -ation		affix length 3


## how to git
echo "# Alpha-Morpho" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/starlight23333/Alpha-Morpho.git
git push -u origin main
