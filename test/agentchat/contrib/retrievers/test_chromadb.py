import os
import pytest
from pathlib import Path
from autogen.agentchat.contrib.retriever.retrieve_utils import (
    split_text_to_chunks,
    extract_text_from_pdf,
    split_files_to_chunks,
    get_files_from_dir,
    is_url,
)

try:
    from autogen.agentchat.contrib.retriever.chromadb import ChromaDB
    import chromadb
except ImportError:
    skip = True
else:
    skip = False

test_dir = Path(__file__).parent.parent.parent.parent / "test_files"


@pytest.mark.skipif(skip, reason="chromadb is not installed")
def test_chromadb(tmpdir):
    # Test index creation and querying
    client = chromadb.PersistentClient(path=tmpdir)
    vectorstore = ChromaDB(path=tmpdir)

    vectorstore.ingest_data(str(test_dir))

    assert client.get_collection("vectorstore")

    results = vectorstore.query(["autogen"])
    assert isinstance(results, dict) and any("autogen" in res[0].lower() for res in results.get("documents", []))

    # Test index_exists()
    vectorstore = ChromaDB(path=tmpdir)
    assert vectorstore.index_exists

    # Test use_existing_index()
    assert vectorstore.collection is None
    vectorstore.use_existing_index()
    assert vectorstore.collection is not None

    vectorstore.ingest_data(str(test_dir), overwrite=True)
    vectorstore.query(["hello"])