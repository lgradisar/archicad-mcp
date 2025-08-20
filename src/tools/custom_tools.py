def init_tools(mcp):
    @mcp.tool(
        name="TestConnection",
        description="Test connection with archicad"
    )
    def test_connection():
        """
        Example of custom tool definition with fastmcp
        """
        from archicad import ACConnection
        conn = ACConnection.connect()
        acc = conn.commands
        act = conn.types
        
        
        return conn
