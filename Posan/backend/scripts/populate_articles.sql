-- SQL Script to populate articles within magazines
-- Run this AFTER magazines are loaded
-- This creates 2-3 articles per magazine

-- Articles for Wild Explorers (magazine_id will vary, adjust based on your data)
-- You'll need to get the actual magazine IDs first with: SELECT id, title FROM magazines;

-- First, let's create articles for magazine ID 1 (Wild Explorers - adjust ID as needed)
INSERT INTO articles (magazine_id, title, content, content_type, age_group, order_in_magazine, reading_time_minutes, created_at)
VALUES 
    (1, 'Amazing Lions of Africa', E'Lions are the kings of the jungle! Did you know that lions are the only cats that live in groups? These groups are called prides.\n\nA pride can have up to 30 lions! The female lions (lionesses) do most of the hunting, while male lions protect the pride with their loud roars. A lion''s roar can be heard from 5 miles away!\n\nLions sleep for about 20 hours a day. They hunt at night when it''s cooler. Baby lions are called cubs, and they love to play and learn from their mothers.', 'ARTICLE', 'EARLY', 1, 3, NOW()),
    
    (1, 'Elephants: Gentle Giants', E'Elephants are the largest land animals on Earth! They can weigh as much as 6 cars and are as tall as a basketball hoop.\n\nElephants are very smart and have amazing memories. They never forget a friend or a place they''ve been. They use their long trunks to drink water, pick up food, and even give hugs!\n\nBaby elephants are called calves. When a calf is born, the whole herd celebrates! Elephants take care of each other and help family members when they''re sick or hurt.', 'ARTICLE', 'EARLY', 2, 3, NOW()),
    
    (2, 'Make a Volcano Experiment', E'Want to make your own volcano at home? It''s easy and super fun!\n\nWhat You Need:\n- Baking soda (2 tablespoons)\n- Vinegar (1/2 cup)\n- Red food coloring\n- A plastic bottle\n- Clay or play dough\n\nHow to Do It:\n1. Put the bottle on a tray\n2. Shape clay around it to look like a mountain\n3. Put baking soda in the bottle\n4. Add a few drops of red food coloring\n5. Pour in the vinegar and watch it erupt!\n\nThe vinegar and baking soda react to create carbon dioxide gas, which makes the ''lava'' bubble out!', 'ACTIVITY', 'MIDDLE', 1, 5, NOW()),
    
    (3, 'My First Numbers', E'Let''s count together! Numbers are everywhere around us.\n\n🍎 One red apple\n🍎🍎 Two red apples  \n🍎🍎🍎 Three red apples\n\nCan you count how many fingers you have? That''s right - 10 fingers!\n\nNumbers help us:\n- Count our toys\n- Know how old we are\n- Share cookies with friends\n\nPractice counting things you see today. How many windows are in your room? How many shoes do you have?', 'ARTICLE', 'TODDLER', 1, 2, NOW()),
    
    (4, 'Journey to Mars', E'Mars is called the Red Planet because it looks red in the sky! But did you know that Mars is actually covered in rust?\n\nIf you could visit Mars, you would see:\n- The tallest mountain in our solar system (3 times taller than Mount Everest!)\n- Huge canyons deeper than the Grand Canyon\n- Two small moons named Phobos and Deimos\n\nA day on Mars is almost the same as Earth - 24 hours and 37 minutes. But a year on Mars is 687 Earth days!\n\nScientists are working on sending people to Mars. Maybe one day YOU could be a Mars explorer!', 'ARTICLE', 'MIDDLE', 1, 4, NOW()),
    
    (5, 'Rainbow Painting Fun', E'Let''s create beautiful rainbow art!\n\nYou Will Need:\n- White paper\n- Watercolors or crayons\n- A paintbrush\n- Water\n\nRainbow Colors in Order:\n🔴 Red\n🟠 Orange  \n🟡 Yellow\n🟢 Green\n🔵 Blue\n🟣 Purple\n\nTry This:\nPaint a big rainbow across your paper. Then add clouds, sunshine, or flowers underneath. Use your imagination!\n\nFun Fact: Rainbows appear when sunlight shines through raindrops in the sky!', 'ACTIVITY', 'EARLY', 1, 3, NOW());

-- Note: Replace the magazine_id values (1, 2, 3, 4, 5) with actual IDs from your magazines table
-- To find the correct IDs, run: SELECT id, title FROM magazines ORDER BY id;
