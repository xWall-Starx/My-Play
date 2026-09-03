-- My Play private music library
-- Run once in the Supabase SQL Editor.

create table if not exists public.music_tracks (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    title text not null,
    artist text not null default 'My Music',
    playlist_name text not null default 'My Golf Playlist',
    storage_path text not null unique,
    mime_type text not null,
    file_size bigint not null check (file_size > 0 and file_size <= 6291456),
    created_at timestamptz not null default now()
);

create index if not exists music_tracks_user_created_idx
    on public.music_tracks (user_id, created_at);

alter table public.music_tracks enable row level security;

drop policy if exists "music_tracks_select_own" on public.music_tracks;
create policy "music_tracks_select_own"
    on public.music_tracks for select
    to authenticated
    using (auth.uid() = user_id);

drop policy if exists "music_tracks_insert_own" on public.music_tracks;
create policy "music_tracks_insert_own"
    on public.music_tracks for insert
    to authenticated
    with check (auth.uid() = user_id);

drop policy if exists "music_tracks_update_own" on public.music_tracks;
create policy "music_tracks_update_own"
    on public.music_tracks for update
    to authenticated
    using (auth.uid() = user_id)
    with check (auth.uid() = user_id);

drop policy if exists "music_tracks_delete_own" on public.music_tracks;
create policy "music_tracks_delete_own"
    on public.music_tracks for delete
    to authenticated
    using (auth.uid() = user_id);

grant select, insert, update, delete on public.music_tracks to authenticated;
grant all on public.music_tracks to service_role;

insert into storage.buckets (
    id,
    name,
    public,
    file_size_limit,
    allowed_mime_types
)
values (
    'Golf-Music',
    'Golf-Music',
    false,
    6291456,
    array['audio/mpeg', 'audio/mp4', 'audio/wav']
)
on conflict (id) do update set
    public = excluded.public,
    file_size_limit = excluded.file_size_limit,
    allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists "golf_music_select_own" on storage.objects;
create policy "golf_music_select_own"
    on storage.objects for select
    to authenticated
    using (
        bucket_id = 'Golf-Music'
        and (storage.foldername(name))[1] = auth.uid()::text
    );

drop policy if exists "golf_music_insert_own" on storage.objects;
create policy "golf_music_insert_own"
    on storage.objects for insert
    to authenticated
    with check (
        bucket_id = 'Golf-Music'
        and (storage.foldername(name))[1] = auth.uid()::text
    );

drop policy if exists "golf_music_delete_own" on storage.objects;
create policy "golf_music_delete_own"
    on storage.objects for delete
    to authenticated
    using (
        bucket_id = 'Golf-Music'
        and (storage.foldername(name))[1] = auth.uid()::text
    );
