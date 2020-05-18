f:
	touch LOLLL
run:
	./NaiveBayesClassifier.sh training.txt testing.txt
dryrun:
	PROD=FALSE python3 finalbak.py training.txt testing.txt
debug:
	PROD=FALSE python3 final.py training.txt testing.txt
clean:
	rm -r  LOLLL *.npy
# python3 NaiveBayesClassifier.py training.txt testing.txt | java -jar validate.jar
