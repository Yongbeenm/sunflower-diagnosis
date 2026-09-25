-- Clean up users: keep only admin, expert, and user
-- Run this with: psql -U sunflower -d sunflower -f cleanup_users.sql
-- Or via docker: docker compose exec -T db psql -U sunflower -d sunflower < scripts/cleanup_users.sql

BEGIN;

-- Show current users before cleanup
SELECT 'Current users before cleanup:' as info;
SELECT id, username, email, role_id FROM users ORDER BY id;

-- Delete all users except admin, expert, and user
DELETE FROM users 
WHERE username NOT IN ('admin', 'expert', 'user');

SELECT 'Users deleted. Remaining:' as info;
SELECT id, username, email, role_id FROM users ORDER BY id;

-- Get role IDs
DO $$
DECLARE
    admin_role_id INT;
    agronomist_role_id INT;
    grower_role_id INT;
    admin_exists BOOLEAN;
    expert_exists BOOLEAN;
    user_exists BOOLEAN;
BEGIN
    -- Get role IDs
    SELECT id INTO admin_role_id FROM roles WHERE name = 'admin';
    SELECT id INTO agronomist_role_id FROM roles WHERE name = 'agronomist';
    SELECT id INTO grower_role_id FROM roles WHERE name = 'grower';
    
    -- Check which users exist
    SELECT EXISTS(SELECT 1 FROM users WHERE username = 'admin') INTO admin_exists;
    SELECT EXISTS(SELECT 1 FROM users WHERE username = 'expert') INTO expert_exists;
    SELECT EXISTS(SELECT 1 FROM users WHERE username = 'user') INTO user_exists;
    
    -- Update or insert admin
    -- Password hash for 'admin' using argon2: $argon2id$v=19$m=65536,t=3,p=4$...
    -- Note: You'll need to run the Python script to get proper argon2 hashes
    IF admin_exists THEN
        UPDATE users 
        SET email = 'admin@example.com', 
            role_id = admin_role_id,
            is_active = true
        WHERE username = 'admin';
        RAISE NOTICE 'Updated admin user';
    ELSE
        INSERT INTO users (email, username, password_hash, role_id, is_active, created_at, updated_at)
        VALUES ('admin@example.com', 'admin', '$argon2id$v=19$m=65536,t=3,p=4$placeholder', admin_role_id, true, NOW(), NOW());
        RAISE NOTICE 'Created admin user';
    END IF;
    
    -- Update or insert expert
    IF expert_exists THEN
        UPDATE users 
        SET email = 'expert@example.com',
            role_id = agronomist_role_id,
            is_active = true
        WHERE username = 'expert';
        RAISE NOTICE 'Updated expert user';
    ELSE
        INSERT INTO users (email, username, password_hash, role_id, is_active, created_at, updated_at)
        VALUES ('expert@example.com', 'expert', '$argon2id$v=19$m=65536,t=3,p=4$placeholder', agronomist_role_id, true, NOW(), NOW());
        RAISE NOTICE 'Created expert user';
    END IF;
    
    -- Update or insert user
    IF user_exists THEN
        UPDATE users 
        SET email = 'user@example.com',
            role_id = grower_role_id,
            is_active = true
        WHERE username = 'user';
        RAISE NOTICE 'Updated user';
    ELSE
        INSERT INTO users (email, username, password_hash, role_id, is_active, created_at, updated_at)
        VALUES ('user@example.com', 'user', '$argon2id$v=19$m=65536,t=3,p=4$placeholder', grower_role_id, true, NOW(), NOW());
        RAISE NOTICE 'Created user';
    END IF;
END $$;

-- Show final users
SELECT 'Final users after cleanup:' as info;
SELECT u.id, u.username, u.email, r.name as role, u.is_active 
FROM users u 
JOIN roles r ON u.role_id = r.id 
ORDER BY u.id;

COMMIT;

-- NOTE: Password hashes are placeholders. You MUST run the Python script to set proper passwords:
-- docker compose exec api python -m scripts.cleanup_users
