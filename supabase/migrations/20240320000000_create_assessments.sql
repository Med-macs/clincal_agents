create table if not exists public.assessments (
    id bigint primary key generated always as identity,
    notes text not null,
    esi_level integer not null,
    diagnosis text not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable Row Level Security (RLS)
alter table public.assessments enable row level security;

-- Create policies
create policy "Enable read access for all users" on public.assessments
    for select
    using (true);

create policy "Enable insert access for authenticated users" on public.assessments
    for insert
    with check (true);

create policy "Enable update access for authenticated users" on public.assessments
    for update
    using (true)
    with check (true);

create policy "Enable delete access for authenticated users" on public.assessments
    for delete
    using (true);

-- Create updated_at trigger
create or replace function public.handle_updated_at()
returns trigger as $$
begin
    new.updated_at = timezone('utc'::text, now());
    return new;
end;
$$ language plpgsql;

create trigger handle_assessments_updated_at
    before update on public.assessments
    for each row
    execute function public.handle_updated_at(); 