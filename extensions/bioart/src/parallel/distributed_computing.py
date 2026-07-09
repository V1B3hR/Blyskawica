#!/usr/bin/env python3
"""
Distributed DNA Computing
Secure, robust distributed computing framework for DNA programs.
"""

import time
import json
import socket
import threading
import ssl
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import logging

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s][%(levelname)s][%(threadName)s] %(message)s"
)
logger = logging.getLogger("DistributedDNAComputer")

# --- SECURE CONFIGURATION ---
MAX_MESSAGE_SIZE = 1024 * 1024  # 1MB per message
HEARTBEAT_TIMEOUT = 60.0        # seconds before node considered stale

class NodeType(Enum):
    COORDINATOR = "coordinator"
    WORKER = "worker"
    HYBRID = "hybrid"

class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class DistributedTask:
    task_id: str
    program: bytes
    input_data: Optional[bytes] = None
    priority: int = 5
    estimated_runtime: float = 1.0
    memory_requirements: int = 256
    assigned_node: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    created_time: float = 0.0
    started_time: Optional[float] = None
    completed_time: Optional[float] = None
    result: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.created_time == 0.0:
            self.created_time = time.time()

@dataclass
class ComputeNode:
    node_id: str
    node_type: NodeType
    address: str
    port: int
    capabilities: Dict[str, Any]
    current_load: float = 0.0
    max_concurrent_tasks: int = 4
    active_tasks: int = 0
    total_completed: int = 0
    total_failed: int = 0
    last_heartbeat: float = 0.0

    def __post_init__(self):
        if self.last_heartbeat == 0.0:
            self.last_heartbeat = time.time()

class DistributedDNAComputer:
    """
    Secure Distributed DNA Computing System
    Coordinates DNA program execution across multiple authenticated nodes.
    """

    def __init__(
        self,
        node_type: NodeType = NodeType.COORDINATOR,
        listen_port: int = 8080,
        node_id: Optional[str] = None,
        ssl_certfile: Optional[str] = None,
        ssl_keyfile: Optional[str] = None,
        auth_token: Optional[str] = None
    ):
        self.node_id = node_id or f"node_{uuid.uuid4().hex[:8]}"
        self.node_type = node_type
        self.listen_port = listen_port
        self.ssl_certfile = ssl_certfile
        self.ssl_keyfile = ssl_keyfile
        self.auth_token = auth_token or uuid.uuid4().hex

        # -- Network --
        self.server_socket = None
        self.running = False
        self.network_thread = None
        self.conn_lock = threading.Lock()
        self.client_connections: Dict[str, socket.socket] = {}

        # -- State --
        self.compute_nodes: Dict[str, ComputeNode] = {}
        self.distributed_tasks: Dict[str, DistributedTask] = {}
        self.task_assignments: Dict[str, str] = {}
        self.global_task_counter = 0

        self.load_balancer = SimpleLoadBalancer()
        self.stats = {
            "total_tasks_submitted": 0,
            "total_tasks_completed": 0,
            "total_tasks_failed": 0,
            "total_nodes_connected": 0,
            "average_task_time": 0.0,
            "network_messages_sent": 0,
            "network_messages_received": 0,
        }

        self.vm_factory = None
        self.local_worker = None
        if node_type in [NodeType.WORKER, NodeType.HYBRID]:
            self.local_worker = LocalWorker(self.node_id)

    def set_vm_factory(self, factory_func: Callable):
        self.vm_factory = factory_func
        if self.local_worker:
            self.local_worker.set_vm_factory(factory_func)

    def start_network_service(self):
        if self.running:
            return
        self.running = True
        self.network_thread = threading.Thread(target=self._network_service_loop, name="NetServiceThread")
        self.network_thread.daemon = True
        self.network_thread.start()
        logger.info(f"DistributedDNAComputer {self.node_id} started on port {self.listen_port} (SSL: {bool(self.ssl_certfile)})")

    def stop_network_service(self):
        self.running = False

        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception as e:
                logger.error(f"Error closing server_socket: {e}")

        with self.conn_lock:
            for conn in self.client_connections.values():
                try:
                    conn.shutdown(socket.SHUT_RDWR)
                    conn.close()
                except Exception as e:
                    logger.error(f"Error closing client connection: {e}")
            self.client_connections.clear()

        if self.network_thread:
            self.network_thread.join(timeout=5.0)

    def register_node(self, node_info: ComputeNode) -> bool:
        with self.conn_lock:
            if node_info.node_id in self.compute_nodes:
                logger.warning(f"Node {node_info.node_id} is already registered.")
                return False
            self.compute_nodes[node_info.node_id] = node_info
            self.stats['total_nodes_connected'] += 1
        logger.info(f"Node {node_info.node_id} registered ({node_info.node_type.value})")
        return True

    def submit_distributed_task(self, program: bytes, input_data: Optional[bytes] = None,
                               priority: int = 5, task_id: Optional[str] = None) -> str:
        if not isinstance(program, bytes) or (input_data is not None and not isinstance(input_data, bytes)):
            raise ValueError("Program and input_data must be bytes.")
        if priority < 1 or priority > 10:
            raise ValueError("Priority must be in 1..10.")

        if task_id is None:
            self.global_task_counter += 1
            task_id = f"dtask_{self.global_task_counter:06d}_{int(time.time())}"

        task = DistributedTask(
            task_id=task_id,
            program=program,
            input_data=input_data,
            priority=priority,
            estimated_runtime=len(program) * 0.001,
            memory_requirements=max(256, len(program) + (len(input_data) if input_data else 0)),
        )
        with self.conn_lock:
            self.distributed_tasks[task_id] = task
            self.stats['total_tasks_submitted'] += 1

        if self.node_type in [NodeType.COORDINATOR, NodeType.HYBRID]:
            self._assign_task_to_node(task)
        return task_id

    def _assign_task_to_node(self, task: DistributedTask):
        with self.conn_lock:
            available_nodes = [
                node for node in self.compute_nodes.values()
                if node.active_tasks < node.max_concurrent_tasks
            ]
        if not available_nodes:
            if self.node_type == NodeType.HYBRID and self.local_worker:
                self._execute_task_locally(task)
                return
            logger.warning(f"No available nodes for task {task.task_id}, queueing...")
            return
        best_node = self.load_balancer.select_node(available_nodes, task)
        if best_node:
            self._send_task_to_node(task, best_node)
        else:
            logger.warning(f"Failed to assign task {task.task_id}")

    def _send_task_to_node(self, task: DistributedTask, node: ComputeNode):
        try:
            message = {
                "type": "execute_task",
                "auth_token": self.auth_token,
                "task_id": task.task_id,
                "program": task.program.hex(),
                "input_data": task.input_data.hex() if task.input_data else None,
                "priority": task.priority,
            }
            if self._send_message_to_node(node.node_id, message):
                task.assigned_node = node.node_id
                task.status = TaskStatus.ASSIGNED
                node.active_tasks += 1
                self.task_assignments[task.task_id] = node.node_id
                logger.info(f"Task {task.task_id} assigned to node {node.node_id}")
            else:
                logger.error(f"Failed to send task {task.task_id} to node {node.node_id}")
        except Exception as e:
            logger.error(f"Error sending task to node: {e}")

    def _execute_task_locally(self, task: DistributedTask):
        if not self.local_worker:
            return
        def local_execution():
            try:
                task.status = TaskStatus.RUNNING
                task.started_time = time.time()
                result = self.local_worker.execute_task(task)
                task.status = TaskStatus.COMPLETED if result.get('success') else TaskStatus.FAILED
                task.completed_time = time.time()
                task.result = result
                if result.get('success'):
                    with self.conn_lock:
                        self.stats['total_tasks_completed'] += 1
                else:
                    with self.conn_lock:
                        self.stats['total_tasks_failed'] += 1
                execution_time = task.completed_time - task.started_time
                self._update_average_task_time(execution_time)
                logger.info(f"Local task {task.task_id} {'completed' if result.get('success') else 'failed'}")
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.completed_time = time.time()
                task.result = {"success": False, "error": str(e)}
                with self.conn_lock:
                    self.stats['total_tasks_failed'] += 1
                logger.error(f"Error executing task locally: {e}")
        execution_thread = threading.Thread(target=local_execution, name=f"LocalTask-{task.task_id}")
        execution_thread.daemon = True
        execution_thread.start()

    def _send_message_to_node(self, node_id: str, message: Dict[str, Any]) -> bool:
        try:
            with self.conn_lock:
                conn = self.client_connections.get(node_id)
            if conn:
                serialized = json.dumps(message).encode('utf-8')
                if len(serialized) > MAX_MESSAGE_SIZE:
                    logger.error(f"Message too long for node {node_id} ({len(serialized)} bytes)")
                    return False
                conn.send(len(serialized).to_bytes(4, 'big'))
                conn.send(serialized)
                with self.conn_lock:
                    self.stats['network_messages_sent'] += 1
                return True
        except Exception as e:
            logger.error(f"Failed to send message to {node_id}: {e}")
        return False

    def _network_service_loop(self):
        try:
            base_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            base_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            base_sock.bind(('0.0.0.0', self.listen_port))
            base_sock.listen(10)
            if self.ssl_certfile and self.ssl_keyfile:
                context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                # Enforce modern TLS versions only (TLS 1.2+)
                if hasattr(context, "minimum_version") and hasattr(ssl, "TLSVersion"):
                    context.minimum_version = ssl.TLSVersion.TLSv1_2
                else:
                    # Fallback for older Python/SSL: disable TLSv1.0 and TLSv1.1 explicitly if available
                    if hasattr(ssl, "OP_NO_TLSv1"):
                        context.options |= ssl.OP_NO_TLSv1
                    if hasattr(ssl, "OP_NO_TLSv1_1"):
                        context.options |= ssl.OP_NO_TLSv1_1
                context.load_cert_chain(certfile=self.ssl_certfile, keyfile=self.ssl_keyfile)
                self.server_socket = context.wrap_socket(base_sock, server_side=True)
            else:
                self.server_socket = base_sock
            while self.running:
                try:
                    self.server_socket.settimeout(2.0)
                    try:
                        client_socket, address = self.server_socket.accept()
                    except socket.timeout:
                        continue

                    logger.info(f"Accepted connection from {address}")
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address),
                        name=f"ClientHandler-{address}"
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except socket.error as err:
                    if self.running:
                        logger.error(f"Socket error in network service: {err}")
        except Exception as e:
            logger.error(f"Network service error: {e}")
        finally:
            if self.server_socket:
                try:
                    self.server_socket.close()
                except Exception:
                    pass

    def _handle_client(self, client_socket: socket.socket, address):
        try:
            while self.running:
                length_data = client_socket.recv(4)
                if not length_data:
                    break
                message_length = int.from_bytes(length_data, 'big')
                if message_length > MAX_MESSAGE_SIZE:
                    logger.error(f"Rejected message from {address}, length={message_length} > {MAX_MESSAGE_SIZE}")
                    break
                message_data = b''
                while len(message_data) < message_length:
                    chunk = client_socket.recv(message_length - len(message_data))
                    if not chunk:
                        break
                    message_data += chunk

                if len(message_data) != message_length:
                    logger.warning(f"Incomplete message from {address}")
                    break
                try:
                    message = json.loads(message_data.decode('utf-8'))
                    self._process_message(message, client_socket)
                    with self.conn_lock:
                        self.stats['network_messages_received'] += 1
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON message from {address}")
                except Exception as e:
                    logger.error(f"Error processing message from {address}: {e}")
        except Exception as e:
            logger.error(f"Client handler error: {e}")
        finally:
            try:
                client_socket.close()
            except Exception:
                pass
            with self.conn_lock:
                for node_id, sock in list(self.client_connections.items()):
                    if sock == client_socket:
                        del self.client_connections[node_id]

    def _process_message(self, message: Dict[str, Any], client_socket: socket.socket):
        # Secure: Check auth for all incoming commands
        msg_type = message.get("type")
        incoming_token = message.get("auth_token")
        if msg_type != "register_node" and incoming_token != self.auth_token:
            self._send_response(client_socket, {"type": "auth_failed", "reason": "Invalid token"})
            logger.warning("Rejected message with invalid auth token.")
            return

        if msg_type == "register_node":
            self._handle_node_registration(message, client_socket)
        elif msg_type == "task_result":
            self._handle_task_result(message)
        elif msg_type == "heartbeat":
            self._handle_heartbeat(message)
        elif msg_type == "node_status":
            self._handle_node_status(message)
        else:
            logger.warning(f"Unknown message type: {msg_type}")

    def _handle_node_registration(self, message: Dict[str, Any], client_socket: socket.socket):
        try:
            node_info = ComputeNode(
                node_id=message["node_id"],
                node_type=NodeType(message["node_type"]),
                address=message["address"],
                port=message["port"],
                capabilities=message.get("capabilities", {}),
                max_concurrent_tasks=message.get("max_concurrent_tasks", 4),
            )
            if self.register_node(node_info):
                with self.conn_lock:
                    self.client_connections[node_info.node_id] = client_socket
                response = {"type": "registration_confirmed", "coordinator_id": self.node_id, "auth_token": self.auth_token}
                self._send_response(client_socket, response)
            else:
                response = {"type": "registration_failed", "reason": "Node already registered"}
                self._send_response(client_socket, response)
        except Exception as e:
            logger.error(f"Node registration error: {e}")

    def _handle_task_result(self, message: Dict[str, Any]):
        task_id = message.get("task_id")
        with self.conn_lock:
            task = self.distributed_tasks.get(task_id)
        if task:
            task.status = TaskStatus.COMPLETED if message.get("success") else TaskStatus.FAILED
            task.completed_time = time.time()
            task.result = message.get("result", {})
            if task.assigned_node in self.compute_nodes:
                node = self.compute_nodes[task.assigned_node]
                node.active_tasks = max(0, node.active_tasks - 1)
                if message.get("success"):
                    node.total_completed += 1
                    self.stats['total_tasks_completed'] += 1
                else:
                    node.total_failed += 1
                    self.stats['total_tasks_failed'] += 1
            if task.started_time:
                execution_time = task.completed_time - task.started_time
                self._update_average_task_time(execution_time)
            logger.info(f"Task {task_id} {'completed' if message.get('success') else 'failed'}")

    def _handle_heartbeat(self, message: Dict[str, Any]):
        node_id = message.get("node_id")
        with self.conn_lock:
            node = self.compute_nodes.get(node_id)
        if node:
            node.last_heartbeat = time.time()
            node.current_load = message.get("current_load", 0.0)
            node.active_tasks = message.get("active_tasks", 0)

    def _handle_node_status(self, message: Dict[str, Any]):
        node_id = message.get("node_id")
        with self.conn_lock:
            node = self.compute_nodes.get(node_id)
        if node:
            node.current_load = message.get('current_load', node.current_load)
            node.active_tasks = message.get('active_tasks', node.active_tasks)

    def _send_response(self, client_socket: socket.socket, response: Dict[str, Any]):
        try:
            serialized = json.dumps(response).encode("utf-8")
            if len(serialized) > MAX_MESSAGE_SIZE:
                logger.error("Response too large to send.")
                return
            client_socket.send(len(serialized).to_bytes(4, 'big'))
            client_socket.send(serialized)
            with self.conn_lock:
                self.stats['network_messages_sent'] += 1
        except Exception as e:
            logger.error(f"Failed to send response: {e}")

    def _update_average_task_time(self, execution_time: float):
        with self.conn_lock:
            completed = self.stats['total_tasks_completed']
            if completed > 0:
                current_avg = self.stats['average_task_time']
                self.stats['average_task_time'] = ((current_avg * (completed - 1)) + execution_time) / completed

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        with self.conn_lock:
            task = self.distributed_tasks.get(task_id)
        if not task:
            return None
        return {
            "task_id": task_id,
            "status": task.status.value,
            "assigned_node": task.assigned_node,
            "created_time": task.created_time,
            "started_time": task.started_time,
            "completed_time": task.completed_time,
            "execution_time": (task.completed_time - task.started_time) if task.started_time and task.completed_time else None,
            "result": task.result,
        }

    def get_system_status(self) -> Dict[str, Any]:
        now = time.time()
        with self.conn_lock:
            nodes = list(self.compute_nodes.values())
            active_nodes = sum(1 for node in nodes if now - node.last_heartbeat < HEARTBEAT_TIMEOUT)
            total_active_tasks = sum(node.active_tasks for node in nodes)
            system_load = sum(node.current_load for node in nodes) / max(1, len(nodes))
            stats_copy = self.stats.copy()
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "total_nodes": len(nodes),
            "active_nodes": active_nodes,
            "total_active_tasks": total_active_tasks,
            "system_load": system_load,
            "statistics": stats_copy,
            "nodes": [
                {
                    "node_id": node.node_id,
                    "node_type": node.node_type.value,
                    "address": f"{node.address}:{node.port}",
                    "active_tasks": node.active_tasks,
                    "current_load": node.current_load,
                    "last_heartbeat_age": now - node.last_heartbeat,
                } for node in nodes
            ],
        }

    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        start_time = time.time()
        while True:
            with self.conn_lock:
                task = self.distributed_tasks.get(task_id)
            if not task:
                return None
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                return {
                    "success": task.status == TaskStatus.COMPLETED,
                    "result": task.result,
                    "execution_time": (
                        (task.completed_time - task.started_time)
                        if task.started_time and task.completed_time else 0
                    ),
                }
            if timeout and (time.time() - start_time) >= timeout:
                return None
            time.sleep(0.1)

class SimpleLoadBalancer:
    """Simple load balancer for task assignment."""

    def select_node(self, available_nodes: List[ComputeNode], task: DistributedTask) -> Optional[ComputeNode]:
        if not available_nodes:
            return None
        scored_nodes = []
        for node in available_nodes:
            load_factor = node.active_tasks / node.max_concurrent_tasks
            memory_factor = 1.0
            if 'max_memory' in node.capabilities:
                memory_factor = min(1.0, node.capabilities['max_memory'] / task.memory_requirements)
            score = load_factor + (1.0 - memory_factor)
            scored_nodes.append((score, node))
        scored_nodes.sort(key=lambda x: x[0])
        return scored_nodes[0][1]

class LocalWorker:
    """Local worker for executing tasks."""

    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.vm_factory = None
        self.active_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0

    def set_vm_factory(self, factory_func: Callable):
        self.vm_factory = factory_func

    def execute_task(self, task: DistributedTask) -> Dict[str, Any]:
        if self.vm_factory is None:
            return {"success": False, "error": "VM factory not set"}
        try:
            self.active_tasks += 1
            vm = self.vm_factory()
            if task.input_data:
                vm.memory[:len(task.input_data)] = task.input_data
            vm.load_program(task.program)
            start_time = time.time()
            vm.run()
            end_time = time.time()
            self.completed_tasks += 1
            return {
                "success": True,
                "execution_time": end_time - start_time,
                "final_registers": getattr(vm, "registers", None),
                "output": getattr(vm, "output_buffer", []),
                "instructions_executed": getattr(vm, "instructions_executed", 0),
                "worker_id": self.worker_id,
            }
        except Exception as e:
            self.failed_tasks += 1
            return {"success": False, "error": str(e), "worker_id": self.worker_id}
        finally:
            self.active_tasks = max(0, self.active_tasks - 1)
