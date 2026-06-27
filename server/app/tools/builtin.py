"""
Built-in Tools
Common utility tools available by default
"""
from typing import Dict, Any, List
import math
import json
from app.tools.base import BaseTool, ToolResult, ToolParameter
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class CalculatorTool(BaseTool):
    """Calculator tool - Perform mathematical operations"""

    def __init__(self):
        """Initialize calculator tool"""
        super().__init__(
            tool_id="calculator",
            name="Calculator",
            description="Perform mathematical calculations",
            version="1.0.0",
            category="utility",
        )

        # Add parameters
        self.add_parameter(
            ToolParameter(
                name="operation",
                type="string",
                description="Operation to perform: add, subtract, multiply, divide, power, sqrt",
                required=True,
            )
        )
        self.add_parameter(
            ToolParameter(
                name="a",
                type="number",
                description="First operand",
                required=True,
            )
        )
        self.add_parameter(
            ToolParameter(
                name="b",
                type="number",
                description="Second operand",
                required=False,
            )
        )

    async def execute(self, **kwargs) -> ToolResult:
        """Execute calculation

        Args:
            operation: Type of calculation
            a: First number
            b: Second number (optional)

        Returns:
            ToolResult with calculation result
        """
        try:
            operation = kwargs.get("operation", "").lower()
            a = kwargs.get("a")
            b = kwargs.get("b")

            result = None

            if operation == "add":
                result = a + b
            elif operation == "subtract":
                result = a - b
            elif operation == "multiply":
                result = a * b
            elif operation == "divide":
                if b == 0:
                    return ToolResult(
                        success=False,
                        error="Cannot divide by zero",
                    )
                result = a / b
            elif operation == "power":
                result = a ** b
            elif operation == "sqrt":
                if a < 0:
                    return ToolResult(
                        success=False,
                        error="Cannot take sqrt of negative number",
                    )
                result = math.sqrt(a)
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown operation: {operation}",
                )

            logger.info(f"Calculation: {a} {operation} {b} = {result}")
            return ToolResult(
                success=True,
                data={"result": result, "operation": operation, "a": a, "b": b},
                metadata={"type": "calculation"},
            )

        except Exception as e:
            logger.error(f"Calculator error: {str(e)}")
            return ToolResult(success=False, error=str(e))


class DataParserTool(BaseTool):
    """Data Parser tool - Parse and validate data formats"""

    def __init__(self):
        """Initialize data parser tool"""
        super().__init__(
            tool_id="data-parser",
            name="Data Parser",
            description="Parse and validate JSON, CSV, and other formats",
            version="1.0.0",
            category="data",
        )

        self.add_parameter(
            ToolParameter(
                name="format",
                type="string",
                description="Data format: json, csv",
                required=True,
            )
        )
        self.add_parameter(
            ToolParameter(
                name="data",
                type="string",
                description="Data to parse",
                required=True,
            )
        )

    async def execute(self, **kwargs) -> ToolResult:
        """Parse data

        Args:
            format: Format type (json, csv)
            data: Data string to parse

        Returns:
            ToolResult with parsed data
        """
        try:
            format_type = kwargs.get("format", "").lower()
            data = kwargs.get("data")

            if format_type == "json":
                parsed = json.loads(data)
                return ToolResult(
                    success=True,
                    data={"parsed": parsed, "format": "json"},
                    metadata={"type": "parsing"},
                )

            elif format_type == "csv":
                lines = data.strip().split("\n")
                if len(lines) < 2:
                    return ToolResult(
                        success=False,
                        error="CSV must have at least header + 1 data row",
                    )

                headers = lines[0].split(",")
                rows = []
                for line in lines[1:]:
                    values = line.split(",")
                    row = {h: v for h, v in zip(headers, values)}
                    rows.append(row)

                return ToolResult(
                    success=True,
                    data={"headers": headers, "rows": rows, "format": "csv"},
                    metadata={"type": "parsing", "row_count": len(rows)},
                )

            else:
                return ToolResult(
                    success=False,
                    error=f"Unsupported format: {format_type}",
                )

        except json.JSONDecodeError as e:
            return ToolResult(
                success=False,
                error=f"Invalid JSON: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Data parser error: {str(e)}")
            return ToolResult(success=False, error=str(e))


class TextTool(BaseTool):
    """Text manipulation tool - String operations"""

    def __init__(self):
        """Initialize text tool"""
        super().__init__(
            tool_id="text-tool",
            name="Text Tool",
            description="Perform text operations: uppercase, lowercase, reverse, count, truncate",
            version="1.0.0",
            category="utility",
        )

        self.add_parameter(
            ToolParameter(
                name="operation",
                type="string",
                description="Operation: uppercase, lowercase, reverse, count, truncate",
                required=True,
            )
        )
        self.add_parameter(
            ToolParameter(
                name="text",
                type="string",
                description="Text to operate on",
                required=True,
            )
        )
        self.add_parameter(
            ToolParameter(
                name="length",
                type="number",
                description="Length for truncate operation",
                required=False,
            )
        )

    async def execute(self, **kwargs) -> ToolResult:
        """Execute text operation

        Args:
            operation: Type of text operation
            text: Text to process
            length: For truncate operation

        Returns:
            ToolResult with processed text
        """
        try:
            operation = kwargs.get("operation", "").lower()
            text = kwargs.get("text", "")

            result = None

            if operation == "uppercase":
                result = text.upper()
            elif operation == "lowercase":
                result = text.lower()
            elif operation == "reverse":
                result = text[::-1]
            elif operation == "count":
                result = len(text)
            elif operation == "truncate":
                length = kwargs.get("length")
                if not isinstance(length, int):
                    return ToolResult(
                        success=False,
                        error="length must be integer for truncate",
                    )
                result = text[:length]
            elif operation == "split":
                delimiter = kwargs.get("delimiter", " ")
                result = text.split(delimiter)
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown operation: {operation}",
                )

            logger.info(f"Text operation: {operation} on text length {len(text)}")
            return ToolResult(
                success=True,
                data={"result": result, "operation": operation},
                metadata={"type": "text_operation"},
            )

        except Exception as e:
            logger.error(f"Text tool error: {str(e)}")
            return ToolResult(success=False, error=str(e))


class ListTool(BaseTool):
    """List operations tool - Sort, filter, transform lists"""

    def __init__(self):
        """Initialize list tool"""
        super().__init__(
            tool_id="list-tool",
            name="List Tool",
            description="Perform list operations: sort, reverse, unique, count, join",
            version="1.0.0",
            category="data",
        )

        self.add_parameter(
            ToolParameter(
                name="operation",
                type="string",
                description="Operation: sort, reverse, unique, count, join, filter",
                required=True,
            )
        )
        self.add_parameter(
            ToolParameter(
                name="items",
                type="string",  # Will be JSON array
                description="List items as JSON array",
                required=True,
            )
        )
        self.add_parameter(
            ToolParameter(
                name="delimiter",
                type="string",
                description="Delimiter for join operation",
                required=False,
                default=",",
            )
        )

    async def execute(self, **kwargs) -> ToolResult:
        """Execute list operation

        Args:
            operation: Type of list operation
            items: List items as JSON
            delimiter: For join operation

        Returns:
            ToolResult with processed list
        """
        try:
            operation = kwargs.get("operation", "").lower()
            items_str = kwargs.get("items", "")

            # Parse items
            try:
                items = json.loads(items_str)
                if not isinstance(items, list):
                    items = [items]
            except:
                items = items_str.split(",")
                items = [i.strip() for i in items]

            result = None

            if operation == "sort":
                result = sorted(items)
            elif operation == "reverse":
                result = list(reversed(items))
            elif operation == "unique":
                result = list(set(items))
            elif operation == "count":
                result = len(items)
            elif operation == "join":
                delimiter = kwargs.get("delimiter", ",")
                result = delimiter.join(str(i) for i in items)
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown operation: {operation}",
                )

            logger.info(f"List operation: {operation} on {len(items)} items")
            return ToolResult(
                success=True,
                data={"result": result, "operation": operation, "count": len(items)},
                metadata={"type": "list_operation"},
            )

        except Exception as e:
            logger.error(f"List tool error: {str(e)}")
            return ToolResult(success=False, error=str(e))
