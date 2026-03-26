-- Run this in Supabase SQL Editor
-- Enables vector support + chat persistence tables.

create extension if not exists vector;

create table if not exists chat_sessions (
    id uuid primary key default gen_random_uuid(),
    title text,
    created_at timestamptz default now()
);

create table if not exists chat_messages (
    id uuid primary key default gen_random_uuid(),
    session_id uuid references chat_sessions(id) on delete cascade,
    role text check (role in ('user', 'assistant', 'system')),
    content text not null,
    created_at timestamptz default now()
);

create index if not exists idx_chat_messages_session_created
on chat_messages(session_id, created_at);
