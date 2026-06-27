"""
Unit tests for Tools
Comprehensive testing of tool functionality
"""
import pytest
from app.tools.base import (
    BaseTool,
    ToolParameter,
    ToolResult,
    ToolRegistry,
    get_tool_registry,
)
from app.tools.builtin import (
    CalculatorTool,
    DataParserTool,
    TextTool,
)


class TestToolParameter:
    """Test ToolParameter"""

    def test_parameter_creation(self):
        """Test creating a parameter"""
        param = ToolParameter(
            name="test",
            type="string",
            description="Test parameter",
            required=True
        )
        assert param.name == "test"
        assert param.required is True

    def test_parameter_to_dict(self):
        """Test parameter serialization"""
        param = ToolParameter("test", "string", "desc")
        data = param.to_dict()
        assert data["name"] == "test"
        assert data["type"] == "string"


class TestToolResult:
    """Test ToolResult"""

    def test_success_result(self):
        """Test creating success result"""
        result = ToolResult(
            success=True,
            data={"value": 42}
        )
        assert result.success is True
        assert result.data["value"] == 42

    def test_error_result(self):
        """Test creating error result"""
        result = ToolResult(
            success=False,
            error="Test error"
        )
        assert result.success is False
        assert result.error == "Test error"

    def test_result_to_dict(self):
        """Test result serialization"""
        result = ToolResult(success=True, data={"x": 1})
        data = result.to_dict()
        assert data["success"] is True
        assert data["data"]["x"] == 1


class TestToolRegistry:
    """Test ToolRegistry"""

    def test_registry_singleton(self):
        """Test registry is singleton"""
        reg1 = get_tool_registry()
        reg2 = get_tool_registry()
        assert reg1 is reg2

    def test_register_tool(self):
        """Test registering a tool"""
        registry = get_tool_registry()
        tool = CalculatorTool()
        registry.register(tool)

        retrieved = registry.get_tool("calculator")
        assert retrieved is not None
        assert retrieved.tool_id == "calculator"

    def test_list_tools(self):
        """Test listing tools"""
        registry = get_tool_registry()
        tools = registry.list_tools()
        assert len(tools) > 0

    def test_unregister_tool(self):
        """Test unregistering a tool"""
        registry = get_tool_registry()
        tool = CalculatorTool()
        registry.register(tool)

        success = registry.unregister("calculator")
        assert success is True


class TestCalculatorTool:
    """Test CalculatorTool"""

    def test_calculator_creation(self):
        """Test creating calculator"""
        tool = CalculatorTool()
        assert tool.tool_id == "calculator"
        assert len(tool.parameters) > 0

    @pytest.mark.asyncio
    async def test_addition(self):
        """Test addition operation"""
        tool = CalculatorTool()
        result = await tool.execute(
            operation="add",
            a=10,
            b=5
        )
        assert result.success is True
        assert result.data["result"] == 15

    @pytest.mark.asyncio
    async def test_division_by_zero(self):
        """Test division by zero error"""
        tool = CalculatorTool()
        result = await tool.execute(
            operation="divide",
            a=10,
            b=0
        )
        assert result.success is False
        assert "zero" in result.error.lower()


class TestDataParserTool:
    """Test DataParserTool"""

    def test_parser_creation(self):
        """Test creating parser"""
        tool = DataParserTool()
        assert tool.tool_id == "data-parser"

    @pytest.mark.asyncio
    async def test_json_parsing(self):
        """Test JSON parsing"""
        tool = DataParserTool()
        result = await tool.execute(
            format="json",
            data='{"name": "test", "value": 42}'
        )
        assert result.success is True

    @pytest.mark.asyncio
    async def test_csv_parsing(self):
        """Test CSV parsing"""
        tool = DataParserTool()
        result = await tool.execute(
            format="csv",
            data="name,age\nJohn,30\nJane,25"
        )
        assert result.success is True


class TestTextTool:
    """Test TextTool"""

    def test_text_tool_creation(self):
        """Test creating text tool"""
        tool = TextTool()
        assert tool.tool_id == "text-tool"

    @pytest.mark.asyncio
    async def test_uppercase(self):
        """Test uppercase operation"""
        tool = TextTool()
        result = await tool.execute(
            operation="uppercase",
            text="hello world"
        )
        assert result.success is True
        assert result.data["result"] == "HELLO WORLD"

    @pytest.mark.asyncio
    async def test_lowercase(self):
        """Test lowercase operation"""
        tool = TextTool()
        result = await tool.execute(
            operation="lowercase",
            text="HELLO WORLD"
        )
        assert result.success is True
        assert result.data["result"] == "hello world"
