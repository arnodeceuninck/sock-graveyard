# Sock Graveyard - Model Package Installation

The ML models have been extracted into a separate package for better modularity.

## For Backend Installation

The backend now depends on the `sock-matcher` model package.

### Option 1: Install as Editable Package (Recommended for Development)

```bash
# From the project root
cd model
pip install -e .
cd ../backend
pip install -r requirements.txt
```

### Option 2: Add to Backend Requirements

Add this line to `backend/requirements.txt`:

```
-e ../model
```

Then install:
```bash
cd backend
pip install -r requirements.txt
```

## For Standalone ML Development

```bash
cd model
pip install -e .
```

See `model/GETTING_STARTED.md` for more details.
