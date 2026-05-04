# Graph Report - .  (2026-05-04)

## Corpus Check
- Corpus is ~5,497 words - fits in a single context window. You may not need a graph.

## Summary
- 149 nodes · 159 edges · 17 communities detected
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 26 edges (avg confidence: 0.81)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Core Bot Lifecycle|Core Bot Lifecycle]]
- [[_COMMUNITY_Revolut DCA Integration|Revolut DCA Integration]]
- [[_COMMUNITY_Firebase Database Service|Firebase Database Service]]
- [[_COMMUNITY_Market Data APIs|Market Data APIs]]
- [[_COMMUNITY_DCA Scheduling Logic|DCA Scheduling Logic]]
- [[_COMMUNITY_Resilient HTTP Client|Resilient HTTP Client]]
- [[_COMMUNITY_Discord Logging System|Discord Logging System]]
- [[_COMMUNITY_HTTP Unit Tests|HTTP Unit Tests]]
- [[_COMMUNITY_Command Handlers|Command Handlers]]
- [[_COMMUNITY_API Client Abstractions|API Client Abstractions]]
- [[_COMMUNITY_Binance Price API|Binance Price API]]
- [[_COMMUNITY_Database Mocks|Database Mocks]]
- [[_COMMUNITY_Bot Instance|Bot Instance]]
- [[_COMMUNITY_Startup Logic|Startup Logic]]
- [[_COMMUNITY_Log Streamer|Log Streamer]]
- [[_COMMUNITY_Documentation|Documentation]]
- [[_COMMUNITY_Metadata Rules|Metadata Rules]]

## God Nodes (most connected - your core abstractions)
1. `Firebase` - 15 edges
2. `RevolutApi` - 8 edges
3. `revolut_dca_task()` - 7 edges
4. `DiscordHandler` - 6 edges
5. `attemptSending()` - 5 edges
6. `LoggingRetry` - 5 edges
7. `Blockchain` - 5 edges
8. `BinanceApi` - 5 edges
9. `ExchangeAPI` - 5 edges
10. `request` - 5 edges

## Surprising Connections (you probably didn't know these)
- `on_ready()` --calls--> `attemptSending()`  [INFERRED]
  main.py → features/utils.py
- `test_revolut_dca_task_skips_if_not_sunday()` --calls--> `revolut_dca_task()`  [INFERRED]
  tests/test_revolut.py → features/revolut_dca/tasks.py
- `test_revolut_dca_task_runs_on_sunday()` --calls--> `revolut_dca_task()`  [INFERRED]
  tests/test_revolut.py → features/revolut_dca/tasks.py
- `test_revolut_dca_task_skips_if_firebase_says_so()` --calls--> `revolut_dca_task()`  [INFERRED]
  tests/test_revolut.py → features/revolut_dca/tasks.py
- `test_revolut_dca_task_insufficient_balance()` --calls--> `revolut_dca_task()`  [INFERRED]
  tests/test_revolut.py → features/revolut_dca/tasks.py

## Hyperedges (group relationships)
- **Bot Feature Initialization Flow** — logging_setup, exchange_rate_setup, btc_mvrv_setup, revolut_dca_setup [INFERRED 0.95]
- **External API Client Layer** — revolut_revolutapi, blockchain_blockchain, binance_binanceapi, apilayer_exchangeapi [INFERRED 0.95]
- **Resilient HTTP Communication** — http_client_request, http_client_get_retry_session, http_client_loggingretry [INFERRED 0.95]

## Communities (21 total, 8 thin omitted)

### Community 0 - "Core Bot Lifecycle"
Cohesion: 0.08
Nodes (8): ping_mvrv(), on_ready(), get_rate_channel_id(), ping_rates(), attemptSending(), run_dca_logic(), test_ping_mvrv(), test_ping_rates()

### Community 1 - "Revolut DCA Integration"
Cohesion: 0.17
Nodes (9): RevolutApi, revolut_dca_task(), is_execution_day(), test_revolut_dca_task_insufficient_balance(), test_revolut_dca_task_runs_on_sunday(), test_revolut_dca_task_skips_if_firebase_says_so(), test_revolut_dca_task_skips_if_not_sunday(), test_revolut_get_gbp_balance_success() (+1 more)

### Community 2 - "Firebase Database Service"
Cohesion: 0.15
Nodes (4): Firebase, test_firebase_dca_skip_decision(), test_firebase_get_profile_rates_exists(), test_firebase_set_profile_rates()

### Community 3 - "Market Data APIs"
Cohesion: 0.18
Nodes (4): ExchangeAPI, Blockchain, test_apilayer_get_rate_success(), test_blockchain_get_mvrv_success()

### Community 4 - "DCA Scheduling Logic"
Cohesion: 0.23
Nodes (5): on_message(), before_revolut_dca_task(), get_next_execution_datetime(), get_seconds_to_next_execution_hour(), get_upcoming_execution_date_str()

### Community 5 - "Resilient HTTP Client"
Cohesion: 0.28
Nodes (7): get_retry_session(), LoggingRetry, Custom Retry class that logs each retry attempt., Creates a requests.Session with retry logic.     Handles retries for both specif, A wrapper around requests.request that provides automatic retries.      By defau, request(), Retry

### Community 7 - "HTTP Unit Tests"
Cohesion: 0.25
Nodes (4): Verify that the retry session is correctly configured with LoggingRetry., Verify that passing retry_config to request() uses a new session with those sett, test_custom_retry_config_integration(), test_retry_configuration()

### Community 8 - "Command Handlers"
Cohesion: 0.25
Nodes (8): BTC MVRV Ping Task, Exchange Rate Command Handler, Exchange Rate Ping Task, Global Message Handler, Revolut DCA Command Handler, Revolut DCA Logic, Exchange Pairs Configuration, Attempt Sending Utility

### Community 9 - "API Client Abstractions"
Cohesion: 0.33
Nodes (7): ExchangeAPI, BinanceApi, Blockchain, get_retry_session, LoggingRetry, request, RevolutApi

## Knowledge Gaps
- **19 isolated node(s):** `Verify that the retry session is correctly configured with LoggingRetry.`, `Verify that passing retry_config to request() uses a new session with those sett`, `Custom Retry class that logs each retry attempt.`, `Creates a requests.Session with retry logic.     Handles retries for both specif`, `A wrapper around requests.request that provides automatic retries.      By defau` (+14 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `run_dca_logic()` connect `Core Bot Lifecycle` to `Revolut DCA Integration`, `DCA Scheduling Logic`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `revolut_dca_task()` connect `Revolut DCA Integration` to `Core Bot Lifecycle`, `DCA Scheduling Logic`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Firebase` (e.g. with `test_firebase_set_profile_rates()` and `test_firebase_get_profile_rates_exists()`) actually correct?**
  _`Firebase` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `RevolutApi` (e.g. with `test_revolut_get_gbp_balance_success()` and `test_revolut_place_order_success()`) actually correct?**
  _`RevolutApi` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `revolut_dca_task()` (e.g. with `is_execution_day()` and `test_revolut_dca_task_skips_if_not_sunday()`) actually correct?**
  _`revolut_dca_task()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `attemptSending()` (e.g. with `on_ready()` and `ping_mvrv()`) actually correct?**
  _`attemptSending()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Verify that the retry session is correctly configured with LoggingRetry.`, `Verify that passing retry_config to request() uses a new session with those sett`, `Custom Retry class that logs each retry attempt.` to the rest of the system?**
  _19 weakly-connected nodes found - possible documentation gaps or missing edges._