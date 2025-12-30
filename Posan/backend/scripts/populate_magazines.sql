-- SQL Script to populate magazines directly in Neon database
-- Run this in your Neon SQL Editor: https://console.neon.tech/

-- Insert sample magazines inspired by popular kids' educational platforms
-- Note: age_group uses enum values: TODDLER (3-5), EARLY (6-8), MIDDLE (9-11), PRETEEN (12-14)

INSERT INTO magazines (title, description, age_group, issue_number, cover_image_url, is_published, publication_date, created_at)
VALUES 
    ('Wild Explorers', 'Discover amazing animals, nature, and wildlife from around the world! Learn fascinating facts about creatures big and small.', 'EARLY', 1, 'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=400&h=600&fit=crop', true, NOW() - INTERVAL '7 days', NOW()),
    ('Science Wizards', 'Become a science wizard! Explore fun experiments, cool inventions, and amazing discoveries that will blow your mind.', 'MIDDLE', 3, 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=400&h=600&fit=crop', true, NOW() - INTERVAL '14 days', NOW()),
    ('Little Learners', 'Fun stories, colorful activities, and simple lessons perfect for our youngest readers! Learning has never been this fun.', 'TODDLER', 5, 'https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=400&h=600&fit=crop', true, NOW() - INTERVAL '3 days', NOW()),
    ('Space Adventures', 'Blast off into space! Learn about planets, stars, astronauts, and the mysteries of the universe in this cosmic journey.', 'MIDDLE', 2, 'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=400&h=600&fit=crop', true, NOW() - INTERVAL '10 days', NOW()),
    ('Creative Minds', 'Unleash your creativity! Art projects, DIY crafts, and fun activities to spark imagination and artistic expression.', 'EARLY', 4, 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=400&h=600&fit=crop', true, NOW() - INTERVAL '5 days', NOW()),
    ('History Heroes', 'Travel back in time and meet amazing historical figures! Discover how people lived in different eras.', 'MIDDLE', 1, 'https://images.unsplash.com/photo-1461360228754-6e81c478b882?w=400&h=600&fit=crop', true, NOW() - INTERVAL '12 days', NOW()),
    ('Math Magicians', 'Make math magical! Fun number games, puzzles, and tricks that make learning math exciting and entertaining.', 'EARLY', 2, 'https://images.unsplash.com/photo-1509228468518-180dd4864904?w=400&h=600&fit=crop', true, NOW() - INTERVAL '8 days', NOW()),
    ('Young Inventors', 'Learn about amazing inventions and how to create your own! Perfect for curious minds who love to build and tinker.', 'PRETEEN', 1, 'https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=400&h=600&fit=crop', true, NOW() - INTERVAL '6 days', NOW()),
    ('Story Time Tales', 'Magical stories, fairy tales, and adventures! Perfect bedtime reading full of wonder and imagination.', 'TODDLER', 7, 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=600&fit=crop', true, NOW() - INTERVAL '2 days', NOW()),
    ('Ocean Explorers', 'Dive deep into the ocean and discover incredible sea creatures, coral reefs, and underwater mysteries!', 'EARLY', 3, 'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=400&h=600&fit=crop', true, NOW() - INTERVAL '9 days', NOW()),
    ('Coding Kids', 'Learn to code through fun games and projects! Build your own apps, games, and digital creations.', 'MIDDLE', 2, 'https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=400&h=600&fit=crop', true, NOW() - INTERVAL '4 days', NOW()),
    ('Planet Earth', 'Explore our amazing planet! Learn about climates, continents, natural wonders, and how to protect our Earth.', 'MIDDLE', 5, 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&h=600&fit=crop', true, NOW() - INTERVAL '11 days', NOW());

-- Verify the data was inserted
SELECT id, title, age_group, issue_number, is_published 
FROM magazines 
ORDER BY created_at DESC;
