-- My Play private Fuel Log
-- Run once in the Supabase SQL Editor.

create table if not exists public.nutrition_logs (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    logged_at timestamptz not null default now(),
    entry_type text not null check (
        entry_type in ('Meal', 'Snack', 'Water', 'Sports drink')
    ),
    description text not null default '',
    water_oz numeric not null default 0 check (
        water_oz >= 0 and water_oz <= 256
    ),
    calories integer check (calories is null or (calories >= 0 and calories <= 10000)),
    notes text not null default '',
    created_at timestamptz not null default now()
);

alter table public.nutrition_logs
    add column if not exists calories integer;

alter table public.nutrition_logs
    drop constraint if exists nutrition_logs_calories_check;
alter table public.nutrition_logs
    add constraint nutrition_logs_calories_check
    check (calories is null or (calories >= 0 and calories <= 10000));

create index if not exists nutrition_logs_user_logged_idx
    on public.nutrition_logs (user_id, logged_at desc);

alter table public.nutrition_logs enable row level security;

drop policy if exists "nutrition_logs_select_own" on public.nutrition_logs;
create policy "nutrition_logs_select_own"
    on public.nutrition_logs for select
    to authenticated
    using (auth.uid() = user_id);

drop policy if exists "nutrition_logs_insert_own" on public.nutrition_logs;
create policy "nutrition_logs_insert_own"
    on public.nutrition_logs for insert
    to authenticated
    with check (auth.uid() = user_id);

drop policy if exists "nutrition_logs_update_own" on public.nutrition_logs;
create policy "nutrition_logs_update_own"
    on public.nutrition_logs for update
    to authenticated
    using (auth.uid() = user_id)
    with check (auth.uid() = user_id);

drop policy if exists "nutrition_logs_delete_own" on public.nutrition_logs;
create policy "nutrition_logs_delete_own"
    on public.nutrition_logs for delete
    to authenticated
    using (auth.uid() = user_id);

grant select, insert, update, delete on public.nutrition_logs to authenticated;
grant all on public.nutrition_logs to service_role;

-- Voluntary, non-diagnostic golf readiness check-ins.
create table if not exists public.performance_checkins (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    sleep_hours numeric not null check (sleep_hours >= 0 and sleep_hours <= 24),
    sleep_quality smallint not null check (sleep_quality between 1 and 5),
    energy smallint not null check (energy between 1 and 5),
    stress smallint not null check (stress between 1 and 5),
    mood smallint not null check (mood between 1 and 5),
    soreness smallint not null check (soreness between 1 and 5),
    notes text not null default '',
    use_for_caddie boolean not null default false,
    created_at timestamptz not null default now()
);

create index if not exists performance_checkins_user_created_idx
    on public.performance_checkins (user_id, created_at desc);

alter table public.performance_checkins enable row level security;

drop policy if exists "performance_checkins_select_own" on public.performance_checkins;
create policy "performance_checkins_select_own"
    on public.performance_checkins for select to authenticated
    using (auth.uid() = user_id);

drop policy if exists "performance_checkins_insert_own" on public.performance_checkins;
create policy "performance_checkins_insert_own"
    on public.performance_checkins for insert to authenticated
    with check (auth.uid() = user_id);

drop policy if exists "performance_checkins_update_own" on public.performance_checkins;
create policy "performance_checkins_update_own"
    on public.performance_checkins for update to authenticated
    using (auth.uid() = user_id)
    with check (auth.uid() = user_id);

drop policy if exists "performance_checkins_delete_own" on public.performance_checkins;
create policy "performance_checkins_delete_own"
    on public.performance_checkins for delete to authenticated
    using (auth.uid() = user_id);

grant select, insert, update, delete on public.performance_checkins to authenticated;
grant all on public.performance_checkins to service_role;
