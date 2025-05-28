create table if not exists public.users (
    id bigint primary key generated always as identity,
    name text not null,
    email text not null unique,
    age integer not null,
    gender text not null,
    user_type text not null check (user_type in ('patient', 'staff')),
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable Row Level Security (RLS)
alter table public.users enable row level security;

-- Create policies
create policy "Enable read access for all users" on public.users
    for select
    using (true);

create policy "Enable insert access for authenticated users" on public.users
    for insert
    with check (true);

create policy "Enable update access for authenticated users" on public.users
    for update
    using (true)
    with check (true);

create policy "Enable delete access for authenticated users" on public.users
    for delete
    using (true);

-- Create updated_at trigger
create trigger handle_users_updated_at
    before update on public.users
    for each row
    execute function public.handle_updated_at();