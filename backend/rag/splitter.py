
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def split_documents(documents: list[Document], chunk_size: int = 1000, chunk_overlap: int = 100) -> list[Document]:
    """
    Splits a list of LangChain Document objects into smaller chunks using
    RecursiveCharacterTextSplitter. Metadata is preserved.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    split_docs = []

    for doc in documents:
        chunks = splitter.split_text(doc.page_content)
        for i, chunk in enumerate(chunks):
            split_docs.append(
                Document(
                    page_content=chunk,
                    metadata={**doc.metadata, "chunk": i}
                )
            )

    return split_docs
