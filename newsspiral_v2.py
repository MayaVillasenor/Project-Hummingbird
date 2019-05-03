# -*- coding: utf-8 -*-
"""NewsSpiral v2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1T32gIT3OElXkE3gglXW4PN-8ef_s3GJQ

# Import Functions
"""

from sklearn import cluster, datasets
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import csv
from sklearn.model_selection import train_test_split
import random

"""# Format Reddit News in CSV"""

redditnews = pd.read_csv('https://raw.githubusercontent.com/Jacobikinz/Project-Hummingbird/master/RedditNews_serialnum.csv', dtype=str,delimiter=',', skiprows=0)

grouped = redditnews.groupby('Date')
list(grouped)
grouped.sum().reset_index().to_csv('weeker_grouped.csv')

#grouped.to_csv(index=False)
#gr = grouped.agg(np.add)
#list(gr)

"""# Plot Data"""

data = pd.read_csv('https://raw.githubusercontent.com/Jacobikinz/Project-Hummingbird/master/CSV_Apple_News_Dates_messed_up.csv', dtype=str,delimiter=',', skiprows=0)
#print (data)
lenny = (data.loc[:,'Close to Close'])
#print (lenny)

#data.keys()
#data['Length of Headlines']

#--------
#Plot apple stock close price over time

plt.scatter(data['date'].astype(int),data['Length of Headlines'].astype(int))

#axes = plt.gca()
#axes.set_xlim([41313,41335])
#axes.set_ylim([60,75])

plt.scatter(data['date'].astype(int),data['Close to Close'].astype(float))

"""# Machine Learning w/Word Count and Difference in Closing price"""

train, test = train_test_split(data, test_size=0.2)

#Training
train_wordcount = (train['Length of Headlines'].values.reshape(-1, 1))
train_close2close = (train['Close to Close'].values.reshape(-1, 1))

#Test
test_wordcount = (test.loc[:,'Length of Headlines'].values.reshape(-1, 1))
test_close2close = (test.loc[:,'Close to Close'].values.reshape(-1, 1))

for i in range(len(train_wordcount)):
  train_wordcount[i]=train_wordcount[i].astype('int32')

for i in range(len(train_close2close)):
  train_close2close[i]=train_close2close[i].astype('float64')

for i in range(len(test_wordcount)):
  test_wordcount[i]=test_wordcount[i].astype('int32')
    
for i in range(len(test_close2close)):
  test_close2close[i]=test_close2close[i].astype('float64')

#---------
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
linregtest = LinearRegression(normalize=True)

linregtest.fit(train_wordcount, train_close2close)
predicted_close = linregtest.predict(test_wordcount)

#R SQUARED
rsq_score = r2_score(test_close2close, predicted_close) 
print ("r^2 for the model:", round(rsq_score,5))
print()

#correlation r value
correlated=pd.DataFrame(test_close2close,columns=['test'])
correlated=pd.concat([correlated,pd.DataFrame(predicted_close,columns=['predicted'])],axis=1)
correlated.astype('float64').corr(method='pearson')

plt.scatter(test_close2close, predicted_close)

"""# Sentiment

https://www.datacamp.com/community/tutorials/simplifying-sentiment-analysis-python
"""

#python -m nltk.downloader all
#pip install nltk
#nltk.download()

"""http://fjavieralba.com/basic-sentiment-analysis-with-python.html"""

import nltk
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')


class Splitter(object):
    def __init__(self):
        self.nltk_splitter = nltk.data.load('tokenizers/punkt/english.pickle')
        self.nltk_tokenizer = nltk.tokenize.TreebankWordTokenizer()

    def split(self, text):
        """
        input format: a paragraph of text
        output format: a list of lists of words.
            e.g.: [['this', 'is', 'a', 'sentence'], ['this', 'is', 'another', 'one']]
        """
        sentences = self.nltk_splitter.tokenize(text)
        tokenized_sentences = [self.nltk_tokenizer.tokenize(sent) for sent in sentences]
        return tokenized_sentences


class POSTagger(object):
    def __init__(self):
        pass
        
    def pos_tag(self, sentences):
        """
        input format: list of lists of words
            e.g.: [['this', 'is', 'a', 'sentence'], ['this', 'is', 'another', 'one']]
        output format: list of lists of tagged tokens. Each tagged tokens has a
        form, a lemma, and a list of tags
            e.g: [[('this', 'this', ['DT']), ('is', 'be', ['VB']), ('a', 'a', ['DT']), ('sentence', 'sentence', ['NN'])],
                    [('this', 'this', ['DT']), ('is', 'be', ['VB']), ('another', 'another', ['DT']), ('one', 'one', ['CARD'])]]
        """

        pos = [nltk.pos_tag(sentence) for sentence in sentences]
        #adapt format
        pos = [[(word, word, [postag]) for (word, postag) in sentence] for sentence in pos]
        return pos
      
      
text = """What can I say about this place. The staff of the restaurant is nice and the eggplant is not bad. Apart from that, very uninspired food, lack of atmosphere and too expensive. I am a staunch vegetarian and was sorely dissapointed with the veggie options on the menu. Will be the last time I visit, I recommend others to avoid."""

splitter = Splitter()
postagger = POSTagger()

splitted_sentences = splitter.split(text)

print (splitted_sentences)

pos_tagged_sentences = postagger.pos_tag(splitted_sentences)

print (pos_tagged_sentences)


class DictionaryTagger(object):
    def __init__(self, dictionary_paths):
        files = [open(path, 'r') for path in dictionary_paths]
        dictionaries = [yaml.load(dict_file) for dict_file in files]
        map(lambda x: x.close(), files)
        self.dictionary = {}
        self.max_key_size = 0
        for curr_dict in dictionaries:
            for key in curr_dict:
                if key in self.dictionary:
                    self.dictionary[key].extend(curr_dict[key])
                else:
                    self.dictionary[key] = curr_dict[key]
                    self.max_key_size = max(self.max_key_size, len(key))

    def tag(self, postagged_sentences):
        return [self.tag_sentence(sentence) for sentence in postagged_sentences]

    def tag_sentence(self, sentence, tag_with_lemmas=False):
        """
        the result is only one tagging of all the possible ones.
        The resulting tagging is determined by these two priority rules:
            - longest matches have higher priority
            - search is made from left to right
        """
        tag_sentence = []
        N = len(sentence)
        if self.max_key_size == 0:
            self.max_key_size = N
        i = 0
        while (i < N):
            j = min(i + self.max_key_size, N) #avoid overflow
            tagged = False
            while (j > i):
                expression_form = ' '.join([word[0] for word in sentence[i:j]]).lower()
                expression_lemma = ' '.join([word[1] for word in sentence[i:j]]).lower()
                if tag_with_lemmas:
                    literal = expression_lemma
                else:
                    literal = expression_form
                if literal in self.dictionary:
                    #self.logger.debug("found: %s" % literal)
                    is_single_token = j - i == 1
                    original_position = i
                    i = j
                    taggings = [tag for tag in self.dictionary[literal]]
                    tagged_expression = (expression_form, expression_lemma, taggings)
                    if is_single_token: #if the tagged literal is a single token, conserve its previous taggings:
                        original_token_tagging = sentence[original_position][2]
                        tagged_expression[2].extend(original_token_tagging)
                    tag_sentence.append(tagged_expression)
                    tagged = True
                else:
                    j = j - 1
            if not tagged:
                tag_sentence.append(sentence[i])
                i += 1
        return tag_sentence

from nltk.tokenize import word_tokenize
tokenized_word=word_tokenize(text)
print(tokenized_word)

import nltk
nltk.download('vader_lexicon')

def nltk_sentiment(sentence):
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    
    nltk_sentiment = SentimentIntensityAnalyzer()
    score = nltk_sentiment.polarity_scores(sentence)
    return score
  

my_sentence = "happy, love, care"#"Barr's theory would create a tyrannical presidency - Washington Examiner/nFacebook bans Alex Jones, Infowars, Louis Farrakhan, and others - Voxcom/nMoore is just the latest casualty of Trump's nomination process - POLITICO/nNow-familiar 'run, hide, fight' put into practice during shooting at UNC Charlotte - NBC News/nTop Executives of Insys, an Opioid Company, Are Found Guilty of Racketeering - The New York Times/n1 Child Dead, 3 People Missing After Migrant Raft Overturns In Rio Grande - NPR/nBaltimore’s Mayor Resigns Over a Series of Self-Published Children’s Books - Slate/nThe river is higher than ever, but is it done climbing? - Quad City Times/nNavy officer sentenced to 9 years in California bridge crash that killed 4 - NBC News/nProtections expanded for doctors with 'conscience' objections to abortions, other procedures - Fox News/nJesse Watters challenges Rep Omar: 'Please say one good thing about America' - Fox News/nKim Jong-nam: Vietnamese woman freed in murder case - BBC News/nScientists Find Small Amount Of Cocaine In UK Shrimp - NPR/nSenate fails to reverse Trump's veto of Yemen resolution - CBS News/nTesla to raise money after painful first quarter with CEO Elon Musk is buying in - USA TODAY/nBurger King spoofs McDonald's with not-so-Happy Meals for Mental Health Month - 10TV/nWeight Watchers shares jump 15% as first-quarter earnings aren't as bad as feared - CNBC/nChecked your Social Security statement? If not, you could miss a shortfall in benefits - USA TODAY/nHoloLens 2 dev kits: $3,500, or $99/month, with Azure credits, Unity trials - Ars Technica/nSamsung now offers up to $400 trade-in toward Galaxy S10, S10 Plus, and S10e (US only) - Android Authority/nSnap selfies with Pikachu in Google Pixel's AR Playground - Engadget/nAdobe's $10 Photography Plan Gone from Site: Cheapest is $20/Month - PetaPixel/nPeter Mayhew, Who Played Chewbacca In 'Star Wars' Films, Dies at 74 - NPR/nDetective Pikachu review — an absurdly silly, wonderful ride - The Verge/n'Game of Thrones' Episode 4 Sneak Peek: Westeros Goes to War for the Iron Throne - Maxim/nMan's year-long quest to pay back the troll who spoiled Infinity War for him comes to beautiful fruition - The AV Club/nStephen Curry dealing with pain, practices without restrictions - Yahoo Sports/nNoah Syndergaard puts his touch on the team Mets have to be - New York Post/nUSWNT's 2019 Women's World Cup Roster Revealed: Brian, Krieger Make Cut - Sports Illustrated/nManny Machado gets swindled out of $300 million by Blooper, the Braves' charlatanic mascot - CBS Sports/nWatch SpaceX launch an ISS resupply mission and make a drone ship landing tonight - TechCrunch/nRunning may have made dinosaurs' wings flap before they evolved to fly: New evidence suggests that passive wing flapping may have arisen earlier than gliding flight - Science Daily/nWhy the 'post-natural' age could be strange and beautiful - BBC News/nEditing Genes To Change Human Traits Is A Tall Order : Shots - Health News - NPR/nMeasles case has cruise ship quarantined in the Caribbean - KCRG/nUtah health officials encourage vaccination, say measles on the way - KSLcom/nBe careful when cracking your neck A 28-year-old man had a stroke popping his neck - CNN/nMeasles Outbreak Confirmed In Allegheny County With Potential Exposure Reported At Pittsburgh International Airport - CBS Pittsburgh/nAt Mueller report hearing, Republicans shift to Clinton and Obama/nJustine Damond: US police officer guilty of murder after shooting Australian yoga teacher trying to report suspected rape/nStudent killed in University of North Carolina-Charlotte shooting &'039;died a hero&'039;/nVenezuela opposition figure, facing arrest warrant, says he met with generals/nUNC Charlotte shooting: Two students killed in deadly campus shooting identified/nJapan welcomes Reiwa &'39;New Year&'39; with hopes for peace, prosperity/nLouisiana&'39;s The Advocate purchasing The Times-Picayune/nSpike in US teen suicides after Netflix &'39;13 Reasons Why&'39; release: study/nHilaria Baldwin fires back at critic who called her &apos;annoying&apos; for sharing miscarriage news/nWilliam Barr, in opening statement, defends handling of Mueller report/nCarnival sued in US over seized property in Cuba, in a first/nCollege admissions scandal: Chinese family &'39;paid $65 million for spot at Stanford University’/nUS says military action &'39;possible&'39; in Venezuela as Kremlin is told to stop meddling/n2 dead, 4 injured in North Carolina campus shooting/nUPDATE 2-McKesson to pay $37 million to resolve West Virginia opioid lawsuit/nJapan&apos;s New Emperor Naruhito Starts Reign at 83% Approval Rating/nThe Rare Porsche Racer Not Built By Porsche/nHomeland Security to use speedy DNA testing to verify migrant family relationships/nAttorney General&apos;s Testimony Shows Why Democrats Are Treading Lightly on Impeachment/nThe Times Cartoon Reveals the Link between Anti-Zionism and Anti-Semitism/nUPDATE 3-Caterpillar gives details on services push, hikes dividend/nVenezuela: three months of crisis/nSan Francisco billionaire gives $30M to study homelessness/nPG&E says SEC investigating it for disclosures, losses for wildfires/nSynagogue didn&'39;t get to fund security upgrades before attack/nThis Volvo P1800ES Is The Only Car You Need To Own/nWho is running for president in 2020? An interactive guide/nDemocrat mocks William Barr&'39;s refusal to attend hearing with bucket of fried chicken: &'39;He&'39;s here!&'39;/nDeutsche Bank Subpoena Deadline Pushed Back to Allow for Hearing/nWill the Culture War Kill the NRA?/nNews details emerge of failed plot to oust Venezuelan president Nicolas Maduro/nUS STOCKS-Wall St drops after Fed chair dampens rate-cut hopes/nFAA mandates changes to Boeing 787 Dreamliner/nSri Lanka mass cancelled over fresh attack fears/n2019 Ford Ranger vs 2020 Jeep Gladiator vs 2019 Chevrolet Colorado vs 2019 Honda Ridgeline/nHoda Kotb admits she &apos;forgot everything&apos; about having a baby and, yes, she Googles/nGoogle Offers Auto-Delete for Location History, Activity Data/nNew York Times editorial board blasts &'39;appalling&'39; anti-Semitic cartoon in Times International edition/nFlorida lawmakers pass bill allowing more armed teachers/nVenezuela crisis: Maduro appears with soldiers following violent protests/nGM considers investing $1 bln in its Missouri plant, state officials say/nBoeing names special adviser to CEO amid 737 MAX crisis/nIsrael&'39;s Netanyahu slams global rise in anti-Semitism/nGoogle Pixel 3a and Pixel 3a XL full specs leak ahead of official reveal/nStarbucks released color-changing cups They&apos;re already selling out/nA Device That Heats Tobacco, But Doesn&apos;t Burn It, Can Now Be Sold in the US Here&apos;s What to Know About IQOS/nPelosi Invokes Obama to Head Off Ocasio-Cortez&apos;s Green New Deal/n5 Reasons You Can&'39;t Beat an F-35 in Combat/nPompeo: US ‘Military Action Is Possible’ in Venezuela/nWhite House letter blasts Mueller report, says Trump has right to instruct advisers not to testify/nFull practice for Curry after dislocating finger/nKanter draws support of union after drawing jeers/nNets' Russell cited for marijuana possession/nHill's lawyer details abuse denial in letter to NFL/nEx-AAU coach gets life in prison for sexual abuse/nCeltics president Ainge suffers mild heart attack/nLowe: Rockets are redefining how basketball is played -- and officiated/nTrash-talking has its place in boxing, but not for Canelo and Jacobs/nLack of defense will make Iaquinta-Cerrone must-watch on Saturday/nWin or lose, the rebuilding Mariners are -- gasp! -- fun to watch/nWhat Noah Syndergaard did is so rare -- it deserves its own name/nUNC a big mover in Way-Too-Early Top 25 for 2019-20/nIs Tony Ferguson next for Conor McGregor?/nYour real estate agent or waiter may just be a professional MMA fighter/nThe future head coach on each Top 25 team/nHow drafting Jarrett Stidham affects Patriots' QB plans/nHow long can baseball's surprising statistical leaders keep it up?/nWhy Jon Lester might be Chicago's best free-agent signing ever/nDon't worry about the Portland Timbers/n2019 Kentucky Derby preview: With Omaha Beach out, field is wide open/nKentucky Derby 2019: The lapsed fan's guide/nIs North Carolina really committed to returning women's basketball to the top?/nAfter 25 years, Kyle Petty is still riding across the country, raising millions/nOver/unders, Super Bowl and playoff odds for all 32 NFL teams/nIs Madrid or Rome a better predictor for the French Open?/nWhat should you expect from incoming rookies?/nSaudi Prince’s Elevation Will Have Far-Reaching Consequences in Energy/nChina Cancels Military Meeting With Vietnam Over Territorial Dispute/nEconomic Scene: Fisticuffs Over the Route to a Clean-Energy Future/nLibya’s Increased Oil Production Thwarts OPEC’s Reduction Plans/nExxon Mobil Lends Its Support to a Carbon Tax Proposal/nBoth Climate Leader and Oil Giant? A Norwegian Paradox/nEnergy Department Closes Office Working on Climate Change Abroad/nOPEC Took Aim at US Oil Producers, but Hurt Itself, Too/nHow Retiring Nuclear Power Plants May Undercut US Climate Goals/nScientists Praise Energy Innovation Office Trump Wants to Shut Down/nOn Nuclear Waste, Finland Shows US How It Can Be Done/nA Stagnant General Electric Will Replace the CEO Who Transformed It/nSettlements for Company Sins Can No Longer Aid Other Projects, Sessions Says/nDrivers Head Into Summer With a Gift at the Gas Pump/nToo Hot to Fly? Climate Change May Take a Toll on Air Travel/nThe US Won’t Actually Leave the Paris Climate Deal Anytime Soon/nFacebook Bars Alex Jones, Louis Farrakhan and Others From Its Services/nTop Executives of Insys, an Opioid Company, Are Found Guilty of Racketeering/nWhere the Good Jobs Are/nWhy Wages Are Finally Rising, 10 Years After the Recession/nTrump Won’t Nominate Stephen Moore for Fed Board/nBeyond Meat’s Share Price Surges on First Day of Trading/nTesla Seeks to Raise $2 Billion in Sale of Stock and Debt/nWheels: Distracted by Tech While Driving? The Answer May Be More Tech/nPG&E Says SEC Is Investigating Its Wildfire Disclosures/nAdmissions Scandal: When ‘Hard Work’ (Plus $65 Million) Helps Get You Into Stanford/nPuerto Rico Seeks to Have $9 Billion in Debt Ruled Unconstitutional/nNew York Times Editorial Page Editor Recuses Himself as Brother Joins 2020 Race/nEconomic View: Manufacturing Can’t Create Enough Jobs Infrastructure Can/nIn Cuba, Carnival Cruise Ships Have Been Using Stolen Ports, Original Owners Say/nBank of England Foresees Faster Economic Growth/nMeanwhile: To Combat Climate Change, Start From the Ground Up (With Dirt)/nFDA Won’t Ban Sales of Textured Breast Implants Linked to Cancer/nCorner Office: Leana Wen of Planned Parenthood Wants to Tackle the ‘Fundamental Unfairness in Our System’/nJack Dorsey Is Gwyneth Paltrow for Silicon Valley/nDealBook Briefing: Capitalists Fear a Socialist Revolt/nWork Friend: How to Handle a ‘Ghost Promotion’ at Work/nCorinne Cobson, Designer With a Rock ’n’ Roll Edge, Dies at 62/nQualcomm Pegs Payment From Apple at $45 Billion to $47 Billion/nDisney and Universal Shore Up Their Benches/nBulletin board: After the Publication of an Anti-Semitic Cartoon, Our Publisher Says We’re Committed to Making Changes/nHow a Canadian Chain Is Reinventing Book Selling/nTimes Disciplines Editor and Cancels Cartoon Contract Over Anti-Semitic Drawing/nNordstrom to Add Two Mini Stores in Its New York Expansion/nFed Leaves Interest Rates Unchanged as Low Inflation Persists/nGavin Williamson, UK Defense Chief, Is Fired Over Huawei Leak/nThe Tax Break Was $260 Million Benefit to the State Was Tiny: $155,520/nLA’s Elite on Edge as Prosecutors Pursue More Parents in Admissions Scandal/nLGBT Households are Now Nielsen Families, and Advertisers and Producers Get a Valuable Tool/nDealBook Briefing: How Deutsche Bank Dealt With Demands for Trump Records/nEmployers Who Talk Up Gender Equity, but Silence Harassment Victims/nLike ‘Uber for Organs’: Drone Delivers Kidney to Maryland Woman/nEric Schmidt to Leave Alphabet Board, Ending an Era That Defined Google/nDrug Agency Calls for Strong Warning Labels on Popular Sleep Aids/nTrilobites: The Microbots Are on Their Way/nFed Likely to Leave Interest Rates Unchanged as Trump Calls for Cut/nin her words: A ‘Women’s New Deal’/nTrump Wants to Block Deutsche Bank From Sharing His Financial Records/nFDA Permits the Sale of IQOS, a New Tobacco Device/nFacebook Unveils Redesign as It Tries to Move Past Privacy Scandals/nInstagram Introduces Shoppable Influencers/nEconomic View: Manufacturing Can’t Create Enough Jobs Infrastructure Can/nWhy Wages Are Finally Rising, 10 Years After the Recession/nTrump Won’t Nominate Stephen Moore for Fed Board/nCalculator: Following the Money in Residential Real Estate/nWhere the Good Jobs Are/nAs Trade Talks Continue, China Is Unlikely to Yield on Control of Data/nFed Likely to Leave Interest Rates Unchanged as Trump Calls for Cut/nH Johannes Witteveen, 97, Dies; Steered IMF Through Turbulent Era/nLabor Dept Says Workers at a Gig Company Are Contractors/nHow Did You Pay for College? We Want to Hear From Readers Around the World/nHow Will the Fed Fight the Next Recession? It’s Trying to Figure That Out Right Now/nWhich Tech Company Is Uber Most Like? Its Answer May Surprise You/nOvercoming Doubts, US Economy Finds a Way Forward/nCannabis, Marijuana, Weed, Pot? Just Call It a Job Machine/nAmericans Are Seeing Highest Minimum Wage in History (Without Federal Help)/nTo TV Writers, Pay Fight With Agents Has Another Villain: Wall Street/nStephen Moore’s Columns Deriding Women Raise New Questions for Trump Fed Pick/nGoogle Employees Say They Faced Retaliation After Organizing Walkout/nAs Herman Cain Bows Out of Fed Contention, Focus Shifts to Stephen Moore/nTrump’s Nafta Revisions Offer Modest Economic Benefits, Report Finds/nEconomic View: Manufacturing Can’t Create Enough Jobs Infrastructure Can/nWhy Wages Are Finally Rising, 10 Years After the Recession/nTrump Won’t Nominate Stephen Moore for Fed Board/nCalculator: Following the Money in Residential Real Estate/nWhere the Good Jobs Are/nAs Trade Talks Continue, China Is Unlikely to Yield on Control of Data/nFed Likely to Leave Interest Rates Unchanged as Trump Calls for Cut/nH Johannes Witteveen, 97, Dies; Steered IMF Through Turbulent Era/nLabor Dept Says Workers at a Gig Company Are Contractors/nHow Did You Pay for College? We Want to Hear From Readers Around the World/nHow Will the Fed Fight the Next Recession? It’s Trying to Figure That Out Right Now/nWhich Tech Company Is Uber Most Like? Its Answer May Surprise You/nOvercoming Doubts, US Economy Finds a Way Forward/nCannabis, Marijuana, Weed, Pot? Just Call It a Job Machine/nAmericans Are Seeing Highest Minimum Wage in History (Without Federal Help)/nTo TV Writers, Pay Fight With Agents Has Another Villain: Wall Street/nStephen Moore’s Columns Deriding Women Raise New Questions for Trump Fed Pick/nGoogle Employees Say They Faced Retaliation After Organizing Walkout/nAs Herman Cain Bows Out of Fed Contention, Focus Shifts to Stephen Moore/nTrump’s Nafta Revisions Offer Modest Economic Benefits, Report Finds/nRate My Portfolio - r/Stocks Quarterly Thread March 2019/nr/Stocks Daily Discussion & Options Trading Thursday - May 02, 2019/nBuffett said Berkshire Hathaway Has Been Buying Shares of $AMZN/nBeyond Meat going live today!/nThe intelligent investor/nElon Musk may buy $10 million of Tesla stock in new offering/nIs a long term index fund a relatively safe investment?/nDisney Stock and Disney+ future defined in 1 paragraph/nSinclair will buy 21 Disney sports networks in a deal valued at more than $10 billion/nBYND Beyond Meat is the future/nWho's in $PLNT/nIf a stock is selling at $70 and it's estimated fair value is $75, would you sell, buy or hold?/nWhere do you look to find an IPO launch date?/nHypothetically speaking    /nPlease help: Emerald Health Therapeutics (EMHTF/EMH)/nWhy has S32L dropped so significantly in the past month?/nCan MSFT get to 200?/nWells Fargo allowed me to open brokerage account then put restriction on it because (they said) I am a foreigner (VN)/nRYT vs QQQ for tech stock ETF's/nNovavax/nRenewable Energy Group (regi)/nIs trading penny stocks an actual thing/nSKT, is it a good buy?/nCan someone clarify what a secondary offering exactly means?/nWhat is the significance in articles like these?/nIs Fitbit (FIT) a deal at $515 a share?/nApple results powering US futures higher, with US stocks set to open in record territory as investors await the Fed/nThe Official r/StockMarket Discord Server Live Chat, link on the right -->/nElon Musk to investors: Self-driving will make Tesla a $500 billion company/nAphria, Trulieve And Aurora Receive Price Upgrades Amid Plans To File CBD Trademarks Following FDA Trials/nBerkshire Hathaway has been buying shares of Amazon, Warren Buffett says/nVegan burger maker Beyond Meat raises price range in upsized IPO/nI'm about to turn 18 and I'm trying to find the best beginning broker, I've been researching how to invest for the last year or so but who should I do it through?/nMajor Averages are Testing their All-Time Highs/nDorel Industries/nThe Fed doesn't react to low inflation/nYETI Positive earnings report = down +10%?/nWhere do you your research from?/nCan someone help me with that Tesla just did?/nA look at Tableau Software, pre results/n$SNRG Confirmation of Shareholder meeting to discuss new partnership (May 15th) Could breakout here/nCan someone explain/nInteresting Interview - are online communities the future of investing?/nThoughts on PINS?/nETFs for steady long term growth/nFed int rates/nOpportunity in healthcare sector/nJust saw chamath's view on tesla What do you guys think? (Video link in description)/nTrading Cosmos (ATOM) on tradeio exchange now with 0 fees (0 taker fee & 0 maker fee) Retweet the post to have chance win $500 Find out more here:/nr/StockMarket May 2019 Stock Picking Contest Google Sheet is now LIVE!/nIs the stock market 'topping out '?/nIf you had to pick between Walmart and AMZN, which would you invest in?/nThoughts on DIS/n"
nltk_sentiment(my_sentence)

#nltk_results = [nltk_sentiment(row) for row in redditnews]
#results_df = pd.DataFrame(nltk_results)
#text_df = pd.DataFrame(redditnews, columns = ['text'])
#nltk_df = text_df.join(results_df)

"""# Extra

https://pypi.org/project/parse/

"2.7.0_bf4fda703454".split("_")

lhs, rhs = "2.7.0_bf4fda703454".split("_", 1)

print(lhs)
print (rhs)

mystring = "What does the fox say?"
mylist = mystring.split(" ")
print (type(mylist))
print (mylist)




pip install PyDictionary
from PyDictionary import PyDictionary

dictionary=PyDictionary()

print (dictionary.meaning("indentation"))
print (dictionary.synonym("Life"))
print (dictionary.antonym("Life"))




text = 'geeks for geeks'
  
# Splits at space 
print(text.split()) 
  
word = 'geeks, for, geeks'
  
# Splits at ',' 
print(word.split(', ')) 
  
word = 'geeks:for:geeks'
  
# Splitting at ':' 
print(word.split(':')) 
  
word = 'CatBatSatFatOr'
  
# Splitting at 3 
print([word[i:i+3] for i in range(0, len(word), 3)]) 



word = 'geeks, for, geeks, pawan'
  
# maxsplit: 0 
print(word.split(', ', 0)) 
  
# maxsplit: 4 
print(word.split(', ', 4)) 
  
# maxsplit: 1 
print(word.split(', ', 1)) 








datar = pd.read_csv('https://raw.githubusercontent.com/Jacobikinz/Project-Hummingbird/master/CSV%20Apple%20%2B%20News%20(RAW).csv', dtype=str,delimiter=',', skiprows=0)
#print (data)

news = (datar.loc[:,'News'])
print (news[30])

hi = "what's up"
print (len(hi))
print (hi + "", 'hi')
print (len(news[30]))
"""