# Kotlin Development Plugin

> Idiomatic Kotlin patterns: coroutines and structured concurrency, Flow / StateFlow / SharedFlow, Kotlin Multiplatform (KMP) shared-code architecture, Jetpack Compose on Android, Ktor server (routing, JWT auth, Exposed, WebSockets), and type-safe DSL design.

## Skills

### `kotlin-specialist`

Senior Kotlin developer covering coroutines, KMP, modern Kotlin 2.x patterns (upstream baseline is Kotlin 1.9+), and the broader Kotlin server/Android/multiplatform ecosystem.

| | |
|---|---|
| **Invoke** | Skill reference |
| **Trigger** | Building or reviewing Kotlin code that uses coroutines, Flow, suspend functions, multiplatform expect/actual, Compose composables, Ktor server routing, sealed-class state modeling, scope functions, or DSL builders |

**Workflow:**
1. Analyze architecture (platform targets, coroutine patterns, shared-code strategy)
2. Design models (sealed classes, data classes, type hierarchies)
3. Implement idiomatic Kotlin (coroutines, Flow, extension functions)
4. Validate with `detekt` and `ktlint`; verify coroutine cancellation
5. Optimize (inline classes, sequence operations, compilation strategies)
6. Test with `runTest` and Turbine

**Reference files:**
| File | Content |
|------|---------|
| coroutines-flow.md | Structured concurrency, scopes/dispatchers, Flow basics and operators, exception handling, cancellation, testing, performance patterns |
| multiplatform-kmp.md | Project structure, Gradle KMP config, expect/actual, shared code patterns, platform-specific implementations, Ktor client multiplatform, source-set hierarchy, native interop |
| android-compose.md | Composables, state management with ViewModel, Material 3 theme, navigation, LazyColumn, side effects, Hilt DI, remember/state, animation, performance |
| ktor-server.md | Application setup, routing, models/serialization, JWT auth, Exposed database integration, error handling, CORS, WebSockets, testing |
| dsl-idioms.md | Type-safe builders, lambda with receiver, scope functions, extension functions, delegated properties, infix functions, operator overloading, sealed classes, inline & reified, `@JvmInline` value classes |

**Source:** Vendored from [Jeffallan/claude-skills](https://github.com/Jeffallan/claude-skills) (MIT). Upstream-synced — see `CLAUDE.md` for the resync workflow.

**Knowledge reference:** Kotlin 2.x (upstream baseline 1.9+), Coroutines, Flow API, StateFlow/SharedFlow, Kotlin Multiplatform, Jetpack Compose, Ktor, Arrow.kt, kotlinx.serialization, Detekt, ktlint, Gradle Kotlin DSL, JUnit 5, MockK, Turbine.

---

**Related:** [libgdx-development](libgdx-development.md) (when building libGDX games in Kotlin) | [tauri-development](tauri-development.md) (alternative for cross-platform desktop/mobile)
