"""Launch Google's server on the explicitly requested notebook instead of scratch.

Only the landing path changes; transport, authentication and tools are Google's.
"""
import colab_mcp
import colab_mcp.session

colab_mcp.session.SCRATCH_PATH = '/drive/1iNPzzxzRtZ5jPw7nodKxehI0xq-LIZvS?authuser=1'
colab_mcp.main()
