"""
Load January 2026 Magazine Editions with Articles
Fresh new content for the new year!
"""
import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
from app.models.content import Magazine, Article, ContentType
from app.models.user import AgeGroup

def create_january_2026_magazines():
    db = SessionLocal()
    
    try:
        print("📰 Creating January 2026 Magazine Editions...\n")
        
        # January 2026 Magazines with Articles
        magazines_data = [
            {
                "magazine": {
                    "title": "New Year Adventures 2026",
                    "description": "Welcome 2026 with exciting stories, new year traditions around the world, and fun resolutions for kids!",
                    "age_group": "6-8",  # AgeGroup.EARLY
                    "issue_number": 1,
                    "cover_image_url": "https://images.unsplash.com/photo-1467810563316-b5476525c0f9?w=400&h=600&fit=crop",
                    "is_published": True,
                    "publication_date": datetime(2026, 1, 1)
                },
                "articles": [
                    {
                        "title": "🎊 How Kids Celebrate New Year Around the World",
                        "content": """Did you know that not everyone celebrates New Year on January 1st? Let's travel around the world and see how different kids celebrate!

**China - Chinese New Year (February 2026)**
Chinese kids celebrate with dragon dances, red lanterns, and lucky money in red envelopes! They also set off fireworks and eat special dumplings.

**India - Multiple New Years**
In India, there are many new year celebrations! During Diwali, kids light diyas (oil lamps) and burst crackers. In spring, they celebrate Holi with colorful powder!

**Scotland - Hogmanay**
Scottish kids stay up late for "first-footing" - where the first person to enter a house brings gifts like coal for warmth!

**Japan - Shogatsu**  
Japanese children fly kites, play traditional games, and eat special mochi (rice cakes). They also write their wishes for the new year!

**Spain - 12 Grapes of Luck**
Spanish kids eat 12 grapes at midnight - one for each month of the year. Each grape represents good luck!

**Fun Activity**: Ask your family how they celebrate New Year. Start your own special family tradition this year!
""",
                        "content_type": ContentType.ARTICLE,
                        "author": "Global Explorer Team",
                        "reading_time_minutes": 5,
                        "age_group": "6-8",
                        "order_in_magazine": 1
                    },
                    {
                        "title": "🎯 Fun New Year Resolutions for Kids",
                        "content": """New Year resolutions don't have to be boring! Here are fun goals you can set for 2026:

**Be a Reading Champion** 📚
Goal: Read 26 books in 2026 (that's 2 books per month!)
Tip: Keep a reading journal with fun stickers!

**Learn Something New** 🎨
Try learning: origami, coding, a musical instrument, or a new language!

**Be Kind Every Day** 💝
Do one kind act daily: help a friend, hug your family, or feed birds.

**Get Moving** ⚽
Exercise goal: 30 minutes of fun activity daily - dance, sports, or bike riding!

**Reduce Screen Time** 📱
Challenge: Replace 30 minutes of screen time with outdoor play or reading.

**Try New Foods** 🥗
Be brave! Try one new fruit or vegetable each week.

**Keep Your Room Tidy** 🧹
Spend 10 minutes each day organizing your space.

**Save Money** 💰
Save a little from your allowance for something special!

Remember: Pick 2-3 goals you really care about. Small steps lead to big achievements!
""",
                        "content_type": ContentType.ARTICLE,
                        "author": "Coach Inspiration",
                        "reading_time_minutes": 4,
                        "age_group": "6-8",
                        "order_in_magazine": 2
                    },
                    {
                        "title": "✨ The Magic of New Beginnings - A Story",
                        "content": """Once upon a time, in a cozy village, there lived a little rabbit named Rosie. 

Rosie was sad because she had made mistakes last year. She forgot her friend Benny's birthday, she didn't practice her carrot-counting homework, and she left her room messy.

On New Year's Eve, Rosie's grandmother gave her a magical calendar. "Every day is a new beginning," Grandma said. "You can start fresh anytime!"

Rosie looked at January 1st. It was blank, waiting for new memories. She smiled and made a plan:

- She would set reminders for friends' birthdays  
- Practice counting every day with real carrots (and eat them after!)
- Tidy her room for 5 minutes each morning

As the clock struck midnight, Rosie made a wish. Not to be perfect, but to try her best and learn from mistakes.

The next morning, Rosie woke up excited. She marked her calendar: "Day 1 of trying my best!"

Her friend Benny hopped by. "Happy New Year, Rosie!"

"Happy New Beginnings, Benny!" Rosie replied with a big smile.

**The Moral**: Every day is a chance to start fresh. Don't worry about yesterday - focus on making today great!
""",
                        "content_type": ContentType.STORY,
                        "author": "Emma Storyteller",
                        "reading_time_minutes": 3,
                        "age_group": "6-8",
                        "order_in_magazine": 3
                    }
                ]
            },
            {
                "magazine": {
                    "title": "Winter Science Wonders 2026",
                    "description": "Explore the amazing science behind winter! Snowflakes, ice, hibernation, and cool experiments you can do at home.",
                    "age_group": "9-11",
                    "issue_number": 1,
                    "cover_image_url": "https://images.unsplash.com/photo-1483728642387-6c3bdd6c93e5?w=400&h=600&fit=crop",
                    "is_published": True,
                    "publication_date": datetime(2026, 1, 10)
                },
                "articles": [
                    {
                        "title": "❄️ The Secret Life of Snowflakes",
                        "content": """Have you ever heard that no two snowflakes are identical? Let's discover why!

**How Snowflakes Form**
Snowflakes begin as tiny ice crystals in clouds. When water vapor freezes around a dust particle, it forms a hexagon (six-sided shape). As it falls, more water vapor freezes onto it, creating beautiful patterns!

**Why Are They All Different?**
Each snowflake travels through different temperatures and humidity levels. Even tiny changes create unique patterns. It's like each snowflake has its own journey through the sky!

**Types of Snowflakes**
- **Stellar Dendrites**: Classic star shapes with six branches
- **Plates**: Flat hexagons  
- **Columns**: Long tubes of ice
- **Needles**: Thin, spike-like crystals
- **Graupel**: Snowflakes covered in ice (like snow pellets)

**Amazing Facts**
🔬 Snowflakes are 95% air, which is why snow feels soft!  
📏 Most snowflakes are 0.5-1 cm across, but some can be 5 cm!  
🌡️ They form best at -12°C to -16°C  
⚡ Thousands of snowflakes can form from one small cloud!

**Home Experiment**
Catch snowflakes on black paper and observe them with a magnifying glass before they melt!
""",
                        "content_type": ContentType.ARTICLE,
                        "author": "Dr. Crystal Ice",
                        "reading_time_minutes": 6,
                        "age_group": "9-11",
                        "order_in_magazine": 1
                    },
                    {
                        "title": "🐻 Winter Survival: How Animals Hibernate",
                        "content": """Ever wondered how bears sleep all winter without eating? Let's explore hibernation!

**What is Hibernation?**
Hibernation is like a deep sleep where animals lower their body temperature and heart rate to save energy when food is scarce.

**Animals That Hibernate**

**Bears** 🐻  
- Don't truly hibernate (they can wake up!)
- Heart rate drops from 50 to 8 beats per minute
- Don't eat, drink, or go to bathroom for months!
- Live off stored body fat

**Ground Squirrels** 🐿️  
- Body temperature drops to almost freezing!  
- Heart beats only 5 times per minute (yours beats 80!)
- Wake up every few weeks to snack on stored food

**Bats** 🦇  
- Hang upside down in caves  
- Breathe only once every 2 hours!
- Can hibernate for 6 months

**Hedgehogs** 🦔  
- Curl into a ball
- Build cozy nests with leaves
- Body temperature drops from 35°C to 10°C!

**Not Hibernation!**
Some animals just sleep more in winter but don't truly hibernate:
- Skunks  
- Raccoons  
- Chipmunks (wake up often to eat stored food)

**Human Connection**
Scientists study hibernating animals to understand how we might survive long space journeys in the future!

**Fun Fact**: Arctic ground squirrels are the only warm-blooded animals that can survive with a body temperature below freezing!
""",
                        "content_type": ContentType.ARTICLE,
                        "author": "Wildlife Biologist Team",
                        "reading_time_minutes": 5,
                        "age_group": "9-11",
                        "order_in_magazine": 2
                    }
                ]
            },
            {
                "magazine": {
                    "title": "Tech Kids 2026 - AI & Robots",
                    "description": "Discover how artificial intelligence and robots are changing our world! Learn about AI, coding, and the future of technology.",
                    "age_group": "12-14",
                    "issue_number": 1,
                    "cover_image_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=600&fit=crop",
                    "is_published": True,
                    "publication_date": datetime(2026, 1, 15)
                },
                "articles": [
                    {
                        "title": "🤖 AI in 2026: How Smart Machines Are Helping Us",
                        "content": """Artificial Intelligence is everywhere in 2026! Let's see how AI makes life better.

**What is AI?**
AI is when computers learn to think and make decisions like humans. Instead of following exact instructions, AI learns from examples and gets smarter over time!

**AI You Use Every Day**

**1. Virtual Assistants** 🗣️
Siri, Alexa, and Google help answer questions and control smart homes.

**2. Recommendation Systems** 🎬
Netflix knows what shows you like, YouTube suggests videos, and Spotify creates playlists just for you!

**3. AI in Gaming** 🎮
NPCs (non-player characters) in video games use AI to react to your moves and play smarter.

**4. Healthcare AI** 🏥
AI helps doctors detect diseases early by analyzing X-rays and medical scans.

**5. Education AI** 📚
Apps like Khan Academy use AI to create personalized learning plans for each student.

**6. Self-Driving Cars** 🚗
AI cars can see pedestrians, other vehicles, and traffic signs to drive safely.

**How Does AI Learn?**

**Machine Learning**: AI looks at thousands of examples. 
Example: Show AI 10,000 cat pictures → AI learns what cats look like!

**Neural Networks**: AI has "brain" layers that process information like our neurons.

**Deep Learning**: Multiple layers help AI understand complex patterns.

**AI Jobs of the Future**
- AI Trainer (teaching AI to be smarter)
- Robot Designer  
- Data Scientist
- AI Ethics Expert
- Prompt Engineer (for AI like ChatGPT!)

**The Cool Part**: By learning about AI now, YOU could create the next big AI invention!

**Try It**: Many websites let you experiment with AI for free - try Scratch (coding with AI blocks) or Teachable Machine (train AI with your webcam!).
""",
                        "content_type": ContentType.ARTICLE,
                        "author": "Tech Future Magazine",
                        "reading_time_minutes": 7,
                        "age_group": "12-14",
                        "order_in_magazine": 1
                    },
                    {
                        "title": "💻 Your First Python Code - Let's Build a Game!",
                        "content": """Ready to create your first Python game? Let's build a Number Guessing Game!

**What You'll Need**
- Computer with Python installed (download from python.org)
- 10 minutes of your time
- Your creativity!

**The Code** (Type this in Python):

```python
import random

# Computer picks a random number
secret_number = random.randint(1, 100)
attempts = 0

print("🎮 Welcome to the Number Guessing Game!")
print("I'm thinking of a number between 1 and 100...")

# Game loop
while True:
    # Get player's guess
    guess = int(input("Your guess: "))
    attempts += 1
    
    # Check if correct
    if guess == secret_number:
        print(f"🎉 You won in {attempts} tries!")
        break
    elif guess < secret_number:
        print("📈 Too low! Try higher.")
    else:
        print("📉 Too high! Try lower.")
```

**How It Works**

1. `import random`: Loads the random number generator
2. `randint(1, 100)`: Picks a number from 1 to 100  
3. `while True`: Creates a loop that runs forever (until we win!)
4. `input()`: Asks player for a guess
5. `if/elif/else`: Checks if guess is correct, too low, or too high

**Level Up Challenges**

**Easy**: Add a lives system (5 mistakes = game over)  
**Medium**: Track the best score (fewest attempts)  
**Hard**: Let player choose difficulty (1-10, 1-100, or 1-1000)  
**Expert**: Add hints like "You're getting warmer!" when close

**Python Concepts You Learned**
✅ Variables (storing data)  
✅ Loops (repeating code)  
✅ Conditionals (if/else decisions)  
✅ User Input  
✅ Random Numbers

**Next Steps**
Once you master this, try:
- Rock, Paper, Scissors game
- Tic-Tac-Toe
- Simple calculator
- Password generator

**The Best Part**: Programming is like magic - you're creating something from nothing with just your ideas and code!

Start coding today at replit.com (free online Python playground)!
""",
                        "content_type": ContentType.ARTICLE,
                        "author": "Code Teacher Pro",
                        "reading_time_minutes": 8,
                        "age_group": "12-14",
                        "order_in_magazine": 2
                    }
                ]
            },
            {
                "magazine": {
                    "title": "Little Explorers - Winter Edition",
                    "description": "Winter fun for little ones! Stories about penguins, snowmen, and cozy winter activities perfect for toddlers.",
                    "age_group": "3-5",
                    "issue_number": 1,
                    "cover_image_url": "https://images.unsplash.com/photo-1548337138-e87d889cc369?w=400&h=600&fit=crop",
                    "is_published": True,
                    "publication_date": datetime(2026, 1, 5)
                },
                "articles": [
                    {
                        "title": "🐧 Penny the Penguin's Snowy Day",
                        "content": """Penny the Penguin woke up to a beautiful snowy morning!

"Wheee!" said Penny as she slid down the icy hill on her tummy.

Penny saw her friend Sammy Seal. "Let's build a snowman!" said Sammy.

They rolled three big snowballs:
- One BIG ball for the body
- One MEDIUM ball for the middle  
- One SMALL ball for the head

Penny found two shiny pebbles for eyes. Sammy found a carrot for the nose!

"We need a scarf!" said Penny. She ran home and brought her red scarf.

"Perfect!" they cheered. Their snowman looked so happy!

Then Penny's tummy rumbled. "Time for fish sticks!" she giggled.

Penny and Sammy waddled home, leaving footprints in the snow.

"Best winter day ever!" they said together.

**The End**

**Questions for Little Ones**:
- What colors are penguins?  
- Have you ever built a snowman?
- What's your favorite winter activity?
""",
                        "content_type": ContentType.STORY,
                        "author": "Little Tales Collection",
                        "reading_time_minutes": 2,
                        "age_group": "3-5",
                        "order_in_magazine": 1
                    },
                    {
                        "title": "❄️ Let's Learn About Winter!",
                        "content": """**What happens in Winter?**

🌨️ **It gets COLD!** Brrr!  
We wear warm coats, hats, and mittens.

❄️ **Snow Falls!**  
Soft, white snowflakes come from the sky.

🌙 **Days are SHORT!**  
The sun goes to bed early. It gets dark sooner.

🐻 **Animals Sleep!**  
Some animals take long naps called hibernation.

**Winter Colors**
- ⚪ White (snow!)
- 🔵 Blue (ice!)
- 💚 Green (pine trees!)
- 🔴 Red (cardinal birds!)

**Fun Winter Activities**
1. Make snow angels
2. Catch snowflakes on your tongue
3. Have hot chocolate
4. Read books under cozy blankets
5. Build a snow fort

**Winter Safety**
👋 Always wear mittens!  
🧣 Keep your neck warm with a scarf!  
🥾 Wear boots in the snow!  
🏠 Come inside when you're too cold!

**Sing Along!**
🎵 "Winter, winter, cold and white,  
Snowflakes falling, what a sight!  
Bundle up and play all day,  
Winter is fun in every way!" 🎵

**Parent Activity**: Go on a winter nature walk and collect pinecones, look for animal tracks in the snow, or count icicles!
""",
                        "content_type": ContentType.ARTICLE,
                        "author": "Early Learning Team",
                        "reading_time_minutes": 3,
                        "age_group": "3-5",
                        "order_in_magazine": 2
                    }
                ]
            }
        ]
        
        # Create magazines and articles
        created_magazines = []
        for mag_data in magazines_data:
            # Create magazine
            magazine = Magazine(**mag_data["magazine"])
            db.add(magazine)
            db.flush()  # Get the magazine ID
            
            # Create articles for this magazine
            for i, article_data in enumerate(mag_data["articles"], 1):
                article = Article(
                    magazine_id=magazine.id,
                    **article_data
                )
                db.add(article)
            
            created_magazines.append(magazine)
            print(f"✅ Created: {magazine.title}")
            print(f"   - {len(mag_data['articles'])} articles added")
            print()
        
        db.commit()
        
        print("=" * 60)
        print(f"🎉 Successfully created {len(created_magazines)} January 2026 magazines!")
        print("=" * 60)
        print("\nMagazines:")
        for mag in created_magazines:
            print(f"  📰 {mag.title}")
            print(f"     Age Group: {mag.age_group.value}")
            print(f"     Issue: #{mag.issue_number}")
            print(f"     Published: {mag.publication_date.strftime('%B %d, %Y')}")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🌟 Loading January 2026 Magazine Content 🌟")
    print("=" * 60)
    create_january_2026_magazines()
    print("\n✨ Magazine loading complete! Check your app to read them!")
