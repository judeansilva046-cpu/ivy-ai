"""
Tests for ETAPA 20: Voice & Computer Control
"""
import pytest
from app.voice.computer_control import (
    ActionType,
    SafetyLevel,
    ComputerAction,
    ComputerVision,
    ScreenCapture,
    SystemAutomation,
    VoiceCommands,
    ControlCenter,
    get_control_center
)


class TestComputerAction:
    """Computer action dataclass tests"""

    def test_computer_action_creation(self):
        """Test creating computer action"""
        action = ComputerAction(
            action_type=ActionType.MOUSE_CLICK,
            parameters={"x": 100, "y": 200},
            safety_level=SafetyLevel.SAFE
        )

        assert action.action_type == ActionType.MOUSE_CLICK
        assert action.parameters["x"] == 100
        assert action.safety_level == SafetyLevel.SAFE
        assert action.timestamp is not None


class TestComputerVision:
    """Computer vision tests"""

    @pytest.mark.asyncio
    async def test_detect_objects(self):
        """Test object detection"""
        vision = ComputerVision()
        objects = await vision.detect_objects("test_image.png")

        assert len(objects) > 0
        assert "object" in objects[0]
        assert "confidence" in objects[0]

    @pytest.mark.asyncio
    async def test_recognize_faces(self):
        """Test face recognition"""
        vision = ComputerVision()
        faces = await vision.recognize_faces("test_image.png")

        assert len(faces) > 0
        assert "face_id" in faces[0]

    @pytest.mark.asyncio
    async def test_extract_text(self):
        """Test OCR text extraction"""
        vision = ComputerVision()
        text = await vision.extract_text("test_image.png")

        assert isinstance(text, str)
        assert len(text) > 0

    @pytest.mark.asyncio
    async def test_understand_scene(self):
        """Test scene understanding"""
        vision = ComputerVision()
        scene = await vision.understand_scene("test_image.png")

        assert "description" in scene
        assert "objects" in scene
        assert "activity" in scene


class TestScreenCapture:
    """Screen capture tests"""

    @pytest.mark.asyncio
    async def test_capture_screen(self):
        """Test screen capture"""
        capture = ScreenCapture()
        filename = await capture.capture_screen()

        assert filename is not None
        assert ".png" in filename

    @pytest.mark.asyncio
    async def test_capture_window(self):
        """Test window capture"""
        capture = ScreenCapture()
        filename = await capture.capture_window("Test Window")

        assert "window" in filename
        assert ".png" in filename

    @pytest.mark.asyncio
    async def test_analyze_screen(self):
        """Test screen analysis"""
        capture = ScreenCapture()
        analysis = await capture.analyze_screen("test_screenshot.png")

        assert "ui_elements" in analysis
        assert "detected_text" in analysis
        assert "interactive_elements" in analysis


class TestSystemAutomation:
    """System automation tests"""

    @pytest.mark.asyncio
    async def test_execute_safe_action(self):
        """Test executing safe action"""
        automation = SystemAutomation()
        action = ComputerAction(
            action_type=ActionType.MOUSE_MOVE,
            parameters={"x": 100, "y": 200},
            safety_level=SafetyLevel.SAFE
        )

        result = await automation.execute_action(action)

        assert result["success"] is True
        assert "action_id" in result

    @pytest.mark.asyncio
    async def test_dangerous_action_blocked(self):
        """Test dangerous action is blocked without approval"""
        automation = SystemAutomation()
        action = ComputerAction(
            action_type=ActionType.FILE_OPERATION,
            parameters={"path": "/sensitive/file"},
            safety_level=SafetyLevel.DANGEROUS
        )

        result = await automation.execute_action(action)

        assert result["success"] is False
        assert "approval" in result["reason"].lower()

    @pytest.mark.asyncio
    async def test_execute_macro(self):
        """Test macro execution"""
        automation = SystemAutomation()
        result = await automation.execute_macro("fill_form", {"name": "John"})

        assert result["success"] is True
        assert "actions_executed" in result

    @pytest.mark.asyncio
    async def test_action_history(self):
        """Test action history tracking"""
        automation = SystemAutomation()
        action = ComputerAction(
            action_type=ActionType.MOUSE_CLICK,
            parameters={"x": 100, "y": 200}
        )

        await automation.execute_action(action)
        history = automation.get_action_history()

        assert len(history) > 0
        assert history[0].action_type == ActionType.MOUSE_CLICK

    @pytest.mark.asyncio
    async def test_undo_action(self):
        """Test undoing last action"""
        automation = SystemAutomation()
        action = ComputerAction(
            action_type=ActionType.MOUSE_CLICK,
            parameters={"x": 100, "y": 200}
        )

        await automation.execute_action(action)
        assert len(automation.get_action_history()) == 1

        await automation.undo_last_action()
        assert len(automation.get_action_history()) == 0


class TestVoiceCommands:
    """Voice command tests"""

    @pytest.mark.asyncio
    async def test_process_voice_command(self):
        """Test voice command processing"""
        voice = VoiceCommands()
        result = await voice.process_voice_command("launch_app Visual Studio Code")

        assert result["success"] is True
        assert "matched_type" in result

    @pytest.mark.asyncio
    async def test_unrecognized_command(self):
        """Test unrecognized command"""
        voice = VoiceCommands()
        result = await voice.process_voice_command("xyz unknown command")

        assert result["success"] is False
        assert result["matched_type"] is None

    def test_command_suggestions(self):
        """Test getting command suggestions"""
        voice = VoiceCommands()
        suggestions = voice.get_command_suggestions("launch")

        assert "launch_app" in suggestions

    @pytest.mark.asyncio
    async def test_command_history(self):
        """Test command history tracking"""
        voice = VoiceCommands()
        await voice.process_voice_command("launch_app Chrome")

        assert len(voice.command_history) == 1


class TestControlCenter:
    """Control center integration tests"""

    def test_initialization(self):
        """Test control center initialization"""
        center = ControlCenter()

        assert center.vision is not None
        assert center.screen is not None
        assert center.automation is not None
        assert center.voice is not None

    @pytest.mark.asyncio
    async def test_handle_voice_command(self):
        """Test handling voice command"""
        center = ControlCenter()
        result = await center.handle_voice_command("screenshot")

        assert "command" in result
        assert "screen_context" in result

    @pytest.mark.asyncio
    async def test_request_approval(self):
        """Test requesting approval"""
        center = ControlCenter()
        action = ComputerAction(
            action_type=ActionType.FILE_OPERATION,
            parameters={"path": "/file"},
            safety_level=SafetyLevel.DANGEROUS
        )

        await center.request_approval(action)

        assert len(center.approval_queue) == 1

    @pytest.mark.asyncio
    async def test_approve_action(self):
        """Test approving action"""
        center = ControlCenter()
        action = ComputerAction(
            action_type=ActionType.MOUSE_CLICK,
            parameters={"x": 100, "y": 200}
        )

        await center.request_approval(action)
        action_id = id(center.approval_queue[0])

        await center.approve_action(action_id)
        assert len(center.approval_queue) == 0

    def test_status(self):
        """Test getting status"""
        center = ControlCenter()
        status = center.get_status()

        assert status["vision_ready"] is True
        assert status["screen_capture_ready"] is True
        assert status["automation_ready"] is True
        assert status["voice_ready"] is True
        assert "pending_approvals" in status

    def test_singleton_instance(self):
        """Test singleton pattern"""
        center1 = get_control_center()
        center2 = get_control_center()
        assert center1 is center2
