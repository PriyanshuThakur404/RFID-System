-- Enable Row Level Security
alter table public.users enable row level security;
alter table public.attendance enable row level security;

-- Create Users Table
create table if not exists public.users (
    id uuid default uuid_generate_v4() primary key,
    uid text unique not null,
    name text not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create Attendance Table
create table if not exists public.attendance (
    id uuid default uuid_generate_v4() primary key,
    user_id uuid references public.users(id),
    uid text not null,
    name text not null,
    date text not null,
    time text not null,
    type text not null default 'RFID',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create indexes for better performance
create index if not exists users_uid_idx on public.users(uid);
create index if not exists attendance_user_id_idx on public.attendance(user_id);
create index if not exists attendance_date_idx on public.attendance(date);
create index if not exists attendance_created_at_idx on public.attendance(created_at);

-- Create policies for Users table
create policy "Allow anonymous read access"
    on public.users
    for select
    to anon
    using (true);

create policy "Allow authenticated insert"
    on public.users
    for insert
    to authenticated
    with check (true);

-- Create policies for Attendance table
create policy "Allow anonymous read access"
    on public.attendance
    for select
    to anon
    using (true);

create policy "Allow authenticated insert"
    on public.attendance
    for insert
    to authenticated
    with check (true);

-- Create function for real-time attendance updates
create or replace function handle_new_attendance()
returns trigger as $$
begin
    perform pg_notify(
        'new_attendance',
        json_build_object(
            'id', new.id,
            'uid', new.uid,
            'name', new.name,
            'date', new.date,
            'time', new.time,
            'type', new.type
        )::text
    );
    return new;
end;
$$ language plpgsql security definer;

-- Create trigger for real-time updates
create trigger on_new_attendance
    after insert on public.attendance
    for each row
    execute procedure handle_new_attendance(); 