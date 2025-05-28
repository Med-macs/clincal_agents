-- Add user_id column to assessments table (nullable initially)
alter table public.assessments 
add column user_id bigint;

-- Create a default user if none exists (for existing assessments)
-- This will be a placeholder user for existing assessments without a user
insert into public.users (name, email, age, gender, user_type) 
values ('System User', 'system@hospital.com', 30, 'male', 'staff')
on conflict (email) do nothing;

-- Temporarily disable the trigger to avoid the updated_at issue
alter table public.assessments disable trigger handle_assessments_updated_at;

-- Update existing assessments to reference the system user
update public.assessments 
set user_id = (select id from public.users where email = 'system@hospital.com' limit 1)
where user_id is null;

-- Re-enable the trigger
alter table public.assessments enable trigger handle_assessments_updated_at;

-- Now make the column not null
alter table public.assessments 
alter column user_id set not null;

-- Add foreign key constraint
alter table public.assessments 
add constraint fk_assessments_user_id 
foreign key (user_id) references public.users(id) on delete cascade;

-- Create index for better query performance
create index idx_assessments_user_id on public.assessments(user_id); 