# Architecture

Three views of `secondbrain`: how the modules fit together, what the entry points
accept, and what a typical session looks like.

## 1. Package map

Modules, the functions they export, and the direction of every import. The package
is a straight three-layer stack — the CLI depends on logging and notes, logging
depends on notes, and `notes.py` depends on nothing but the standard library.

```mermaid
---
title: Module and function map
---
flowchart LR
    subgraph entry["Entry points"]
        direction TB
        script["<b>pyproject.toml</b><br/>project.scripts<br/><code>secondbrain</code>"]
        dunder["<b>__main__.py</b><br/>python -m secondbrain"]
    end

    subgraph cli_layer["CLI layer — cli.py"]
        direction TB
        cli_grp["<code>cli</code><br/>click.group"]
        cmd_new["<code>new</code>"]
        cmd_list["<code>list_notes</code>"]
        cmd_show["<code>show</code>"]
    end

    subgraph log_layer["Logging — app.py"]
        direction TB
        conf["<code>configure_logging</code>"]
        appmain["<code>main</code><br/>demo greeting"]
        fmt["<code>LOG_FORMAT</code><br/><code>LEVEL_ICONS</code>"]
    end

    subgraph core["Core logic — notes.py"]
        direction TB
        ndir["<code>notes_dir</code>"]
        slug["<code>slugify</code>"]
        build["<code>build_note_path</code>"]
        create["<code>create_note</code>"]
        read["<code>read_note</code>"]
    end

    subgraph ext["Third-party"]
        direction TB
        click_lib["click"]
        loguru_lib["loguru"]
    end

    subgraph store["Filesystem"]
        direction TB
        notes_md["SECONDBRAIN_DIR<br/>*.md notes"]
        logfile["LOG_FILE<br/>app.log"]
    end

    script --> cli_grp
    dunder --> cli_grp

    cli_grp --> cmd_new
    cli_grp --> cmd_list
    cli_grp --> cmd_show
    cli_grp -->|"import"| conf

    cmd_new --> create
    cmd_new --> ndir
    cmd_list --> ndir
    cmd_show --> ndir
    cmd_show --> read

    create --> build
    build --> slug
    create --> notes_md
    read --> notes_md

    conf --> ndir
    conf --> fmt
    conf --> logfile
    appmain --> conf

    click_lib -.-> cli_grp
    loguru_lib -.-> conf
    loguru_lib -.-> cmd_new
```

!!! note "Reading the edges"
    Solid arrows are calls or command registrations; dotted arrows are third-party
    libraries providing the machinery. `notes.py` sits at the bottom with no
    internal dependencies, which is why it is the easiest module to test and extend.

## 2. Entry points and arguments

Every way into the program converges on the same Click group. Configuration is read
from the environment on each call, so nothing is frozen at import time.

```mermaid
---
title: Entry points, arguments, and behaviour
---
flowchart LR
    subgraph invoke["Invocation"]
        direction TB
        i1["<code>uv run secondbrain ...</code>"]
        i2["<code>python -m secondbrain ...</code>"]
        i3["<code>uv run --env-file .env ...</code>"]
    end

    group["<b>cli</b> — click.group<br/>calls configure_logging<br/>before any subcommand"]

    subgraph env["Environment variables"]
        direction TB
        e1["<code>SECONDBRAIN_DIR</code><br/>default ~/secondbrain/"]
        e2["<code>LOG_LEVEL</code><br/>default INFO"]
        e3["<code>LOG_FILE</code><br/>default DIR/app.log"]
    end

    subgraph cmds["Subcommands"]
        direction TB
        c_new["<b>new TITLE</b><br/>required string"]
        c_list["<b>list</b><br/>no arguments"]
        c_show["<b>show NUMBER</b><br/>required int"]
    end

    subgraph behind["What happens behind them"]
        direction TB
        b_new["slugify title<br/>build DATE-slug.md<br/>de-duplicate with -1, -2<br/>write heading + timestamp<br/>echo absolute path"]
        b_list["glob *.md<br/>sort reverse, newest first<br/>echo numbered list"]
        b_show["glob + sort<br/>index NUMBER - 1<br/>echo file contents"]
    end

    subgraph exits["Exit behaviour"]
        direction TB
        ok["exit 0"]
        fail["exit 1<br/>message on stderr"]
    end

    i1 --> group
    i2 --> group
    i3 --> group

    e1 -.-> group
    e2 -.-> group
    e3 -.-> group

    group --> c_new
    group --> c_list
    group --> c_show

    c_new --> b_new
    c_list --> b_list
    c_show --> b_show

    b_new --> ok
    b_list --> ok
    b_show --> ok
    b_show --> fail
```

!!! warning "Missing directory is handled differently per command"
    `list` prints a plain message and still exits 0. `show` treats the same
    situation as an error: message on stderr, exit code 1. `new` never hits the
    case at all, because it creates the directory on the way through.

## 3. Example user flow

A first session: capture two ideas, look at what is stored, read one back.

```mermaid
---
title: Typical capture-and-review session
---
flowchart LR
    subgraph setup["One-time setup"]
        direction TB
        s1["<code>uv sync</code>"]
        s2["<code>cp .env.example .env</code>"]
    end

    subgraph capture["Capture"]
        direction TB
        u1["<code>secondbrain new<br/>'My brilliant idea'</code>"]
        r1["writes<br/>2026-08-02-my-brilliant-idea.md<br/>prints the path"]
        u2["<code>secondbrain new<br/>'Café notes'</code>"]
        r2["accents folded<br/>2026-08-02-cafe-notes.md"]
    end

    subgraph review["Review"]
        direction TB
        u3["<code>secondbrain list</code>"]
        r3["1. 2026-08-02-my-brilliant-idea.md<br/>2. 2026-08-02-cafe-notes.md"]
    end

    subgraph readback["Read back"]
        direction TB
        u4["<code>secondbrain show 1</code>"]
        r4["# My brilliant idea<br/>2026-08-02T18:20:14"]
    end

    dup{"same title<br/>same day?"}
    dup_yes["saved as<br/>...-idea-1.md<br/>nothing overwritten"]

    oor{"NUMBER<br/>in range?"}
    oor_no["Error: Note N not found.<br/>exit 1"]

    s1 --> s2 --> u1
    u1 --> dup
    dup -->|no| r1
    dup -->|yes| dup_yes
    r1 --> u2 --> r2 --> u3 --> r3 --> u4
    u4 --> oor
    oor -->|yes| r4
    oor -->|no| oor_no
```

!!! tip "Numbering is positional, not permanent"
    `list` numbers notes newest-first each time it runs, so a number is only valid
    until the next note is created. Re-run `list` before `show` if anything has
    changed in between.
