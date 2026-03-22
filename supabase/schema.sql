-- ============================================================================
-- AscendFi / AI Financial — Supabase schema
-- Run in: Supabase Dashboard → SQL Editor (or `supabase db push` with CLI)
-- Auth: Supabase Auth (`auth.users`). All app tables use `user_id = auth.uid()`.
-- ============================================================================

-- ── Optional: tighten timestamps (Supabase projects usually have this) ──────
-- create extension if not exists pgcrypto; -- gen_random_uuid()

-- ============================================================================
-- 1. PROFILES (1:1 with auth.users)
--    Sync legal name + state from signup user_metadata, or edit here.
-- ============================================================================

create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  legal_first_name text,
  legal_last_name text,
  state_code char(2),
  display_name text,
  monthly_income numeric(14, 2),
  checking_balance numeric(14, 2) default 0,
  savings_balance numeric(14, 2) default 0,
  credit_score int,
  net_worth numeric(14, 2),
  life_events text[] default '{}',
  extra jsonb default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

comment on table public.profiles is 'Core user financial snapshot; extends auth.users.';

create index if not exists profiles_state_code_idx on public.profiles (state_code);

-- Auto-create profile on signup
create or replace function public.handle_new_user ()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, legal_first_name, legal_last_name, state_code, display_name)
  values (
    new.id,
    new.raw_user_meta_data->>'legal_first_name',
    new.raw_user_meta_data->>'legal_last_name',
    nullif(new.raw_user_meta_data->>'state', ''),
    trim(
      coalesce(new.raw_user_meta_data->>'legal_first_name', '') || ' ' ||
      coalesce(new.raw_user_meta_data->>'legal_last_name', '')
    )
  );
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user ();

-- Keep updated_at fresh
create or replace function public.set_updated_at ()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists profiles_updated_at on public.profiles;
create trigger profiles_updated_at
  before update on public.profiles
  for each row execute function public.set_updated_at ();

-- ============================================================================
-- 2. DEBTS (matches backend Bill/Debt-style models + dashboard debts[])
-- ============================================================================

create table if not exists public.debts (
  id uuid primary key default gen_random_uuid (),
  user_id uuid not null references auth.users (id) on delete cascade,
  name text not null,
  balance numeric(14, 2) not null default 0,
  interest_rate numeric(8, 4) not null default 0,
  minimum_payment numeric(14, 2) not null default 0,
  debt_type text not null default 'other',
  sort_order int not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists debts_user_id_idx on public.debts (user_id);

drop trigger if exists debts_updated_at on public.debts;
create trigger debts_updated_at
  before update on public.debts
  for each row execute function public.set_updated_at ();

-- ============================================================================
-- 3. BILLS (backend FinancialContext.bills)
-- ============================================================================

create table if not exists public.bills (
  id uuid primary key default gen_random_uuid (),
  user_id uuid not null references auth.users (id) on delete cascade,
  name text not null,
  amount numeric(14, 2) not null,
  due_date date not null,
  category text not null default 'general',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists bills_user_id_due_date_idx on public.bills (user_id, due_date);

drop trigger if exists bills_updated_at on public.bills;
create trigger bills_updated_at
  before update on public.bills
  for each row execute function public.set_updated_at ();

-- ============================================================================
-- 4. TRANSACTIONS / SPENDING (backend SpendingEntry + dashboard recentActivity)
--     Positive amount = inflow (income); negative = outflow (expense).
-- ============================================================================

create table if not exists public.transactions (
  id uuid primary key default gen_random_uuid (),
  user_id uuid not null references auth.users (id) on delete cascade,
  occurred_on date not null default (current_date),
  amount numeric(14, 2) not null,
  category text not null,
  description text,
  created_at timestamptz not null default now()
);

create index if not exists transactions_user_occurred_idx on public.transactions (user_id, occurred_on desc);

-- ============================================================================
-- 5. RISK INDICATORS (dashboard RiskGauge rows — optional denormalized cache)
-- ============================================================================

create table if not exists public.risk_indicators (
  id uuid primary key default gen_random_uuid (),
  user_id uuid not null references auth.users (id) on delete cascade,
  slug text not null,
  probability numeric(5, 4) not null check (probability >= 0 and probability <= 1),
  level text not null check (level in ('low', 'moderate', 'high', 'critical')),
  label text not null,
  factors jsonb not null default '[]'::jsonb,
  updated_at timestamptz not null default now(),
  unique (user_id, slug)
);

create index if not exists risk_indicators_user_id_idx on public.risk_indicators (user_id);

-- ============================================================================
-- 6. CHART SERIES (debt timeline, financial gains — JSON matches LineChart datasets)
--     Alternatively compute in API; this stores precomputed series per user.
-- ============================================================================

create table if not exists public.financial_chart_series (
  id uuid primary key default gen_random_uuid (),
  user_id uuid not null references auth.users (id) on delete cascade,
  series_key text not null,
  labels jsonb not null default '[]'::jsonb,
  datasets jsonb not null default '[]'::jsonb,
  updated_at timestamptz not null default now(),
  unique (user_id, series_key)
);

comment on table public.financial_chart_series is 'e.g. series_key = debt_timeline | financial_gains | paycheck_split';

-- ============================================================================
-- 7. CHAT (optional persistence; app currently uses agent session — add later)
-- ============================================================================

create table if not exists public.chat_sessions (
  id uuid primary key default gen_random_uuid (),
  user_id uuid not null references auth.users (id) on delete cascade,
  title text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists chat_sessions_user_id_idx on public.chat_sessions (user_id, created_at desc);

drop trigger if exists chat_sessions_updated_at on public.chat_sessions;
create trigger chat_sessions_updated_at
  before update on public.chat_sessions
  for each row execute function public.set_updated_at ();

create table if not exists public.chat_messages (
  id uuid primary key default gen_random_uuid (),
  session_id uuid not null references public.chat_sessions (id) on delete cascade,
  role text not null check (role in ('user', 'assistant', 'system')),
  content text not null,
  created_at timestamptz not null default now()
);

create index if not exists chat_messages_session_id_idx on public.chat_messages (session_id, created_at);

-- ============================================================================
-- ROW LEVEL SECURITY
-- ============================================================================

alter table public.profiles enable row level security;
alter table public.debts enable row level security;
alter table public.bills enable row level security;
alter table public.transactions enable row level security;
alter table public.risk_indicators enable row level security;
alter table public.financial_chart_series enable row level security;
alter table public.chat_sessions enable row level security;
alter table public.chat_messages enable row level security;

-- Profiles: users read/update own row
create policy "profiles_select_own" on public.profiles for select using (auth.uid () = id);
create policy "profiles_update_own" on public.profiles for update using (auth.uid () = id);
-- Insert handled by trigger from auth; if you insert manually in SQL, use service role

-- Debts, bills, transactions, risks, charts
create policy "debts_all_own" on public.debts for all using (auth.uid () = user_id);
create policy "bills_all_own" on public.bills for all using (auth.uid () = user_id);
create policy "transactions_all_own" on public.transactions for all using (auth.uid () = user_id);
create policy "risk_indicators_all_own" on public.risk_indicators for all using (auth.uid () = user_id);
create policy "financial_chart_series_all_own" on public.financial_chart_series for all
  using (auth.uid () = user_id);

-- Chat: own sessions; messages via session ownership
create policy "chat_sessions_all_own" on public.chat_sessions for all using (auth.uid () = user_id);

create policy "chat_messages_select_own" on public.chat_messages for select using (
  exists (
    select 1 from public.chat_sessions s
    where s.id = chat_messages.session_id and s.user_id = auth.uid ()
  )
);

create policy "chat_messages_insert_own" on public.chat_messages for insert with check (
  exists (
    select 1 from public.chat_sessions s
    where s.id = session_id and s.user_id = auth.uid ()
  )
);

create policy "chat_messages_update_own" on public.chat_messages for update using (
  exists (
    select 1 from public.chat_sessions s
    where s.id = chat_messages.session_id and s.user_id = auth.uid ()
  )
);

create policy "chat_messages_delete_own" on public.chat_messages for delete using (
  exists (
    select 1 from public.chat_sessions s
    where s.id = chat_messages.session_id and s.user_id = auth.uid ()
  )
);

-- ============================================================================
-- GRANTS (authenticated users use Supabase client with JWT)
-- ============================================================================

grant usage on schema public to anon, authenticated;
grant select, insert, update, delete on all tables in schema public to authenticated;
grant usage, select on all sequences in schema public to authenticated;
