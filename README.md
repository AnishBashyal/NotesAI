# LectureToNotes.ai

**Inspiration**

Tired of information overload during lengthy lectures?​ Struggling to maintain your focus for extended periods?​ Experiencing hearing difficulties?​

Introducing, LectureToNotesAI, your solution.​
​
LectureToNotesAI is an intelligent speech-to-text conversion tool where​ users can upload video or audio files of lectures and, in return, receive concise bullet notes of the content. Our goal is clear: improve the accessibility and usability of all spoken content, and ultimately save time and effort.

**What it does**

Our project first converts video to audio, and then transcribes it using Google Cloud’s Text to Speech API. This transcript is then fed with prompt engineering to OpenAI’s Large Language Model(LLM) via LangChain to summarize it. We style the summary into bullet points for the user, and maintain a tracking platform for the history of their notes.


**How we built it**

We made Flask the backbone of our project, and integrated it with many different APIs and tech tools. We authenticated the users using Auth0 and hosted their data in the Cloud using Firebase. At such a great time of open and cool APIs, we tried to incorporate them to the best of our potential and also added a taste of AI to our program.


**Challenges we ran into**

- Multiple layers of conversions. Video -> Audio -> Transcript -> Summary -> Bullets.
- API restrictions (i.e: OpenAI’s 3 requests per min quota)

**Accomplishments that we're proud of**

- Completing a project in our first hackathon (It finally worked!)
- Familiarizing ourselves with new technologies such as Auth0, Firebase, and integrating them 
- Making something that benefits students 

**What we learned**

- Working with file conversions
- New APIs and tech tools
- Learned to collaborate with peers and effectively use Github

**What's next for LectureToNotes.ai**

- Allow users to share and combine notes with each other 
- Multilingual support
- Allow users to customize the prompts, and personalize style of notes to their preference
