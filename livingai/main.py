"""
LivingAI V1+V2 Main Entry Point
===============================

Main entry point for the LivingAI Agentic AI Operating Environment.
Provides CLI and programmatic access to the LivingAI system.
"""

import sys
import argparse
import logging
from typing import Dict, Any, Optional

from livingai.agentic_loop import agentic_loop
from livingai.tools.integration import tools_integration
from livingai.agents.manager import AgentManager
from livingai.config import Config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for LivingAI."""
    parser = argparse.ArgumentParser(
        description='LivingAI V1+V2 - Local-First Agentic AI Operating Environment'
    )
    
    # Main commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start the agentic loop')
    start_parser.add_argument(
        '--interval',
        type=float,
        default=1.0,
        help='Time between cycles in seconds (default: 1.0)'
    )
    start_parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to configuration file'
    )
    
    # Stop command
    subparsers.add_parser('stop', help='Stop the agentic loop')
    
    # Run once command
    subparsers.add_parser('once', help='Run one cycle of the agentic loop')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    # Tools command
    tools_parser = subparsers.add_parser('tools', help='Manage tools')
    tools_subparsers = tools_parser.add_subparsers(dest='tools_command', help='Tools commands')
    tools_subparsers.add_parser('list', help='List available tools')
    tools_subparsers.add_parser('info', help='Show tool information')
    
    # Agents command
    agents_parser = subparsers.add_parser('agents', help='Manage agents')
    agents_subparsers = agents_parser.add_subparsers(dest='agents_command', help='Agents commands')
    agents_subparsers.add_parser('list', help='List agents')
    agents_subparsers.add_parser('status', help='Show agent status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Load configuration
    config = {}
    if hasattr(args, 'config') and args.config:
        config = Config.load(args.config)
    
    # Handle commands
    if args.command == 'start':
        logger.info("Starting LivingAI Agentic Loop...")
        loop = agentic_loop
        loop.run_continuous(interval=args.interval)
        logger.info(f"Agentic loop started with interval={args.interval}s")
        logger.info("Press Ctrl+C to stop")
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            loop.stop()
            logger.info("Agentic loop stopped")
    
    elif args.command == 'stop':
        logger.info("Stopping LivingAI Agentic Loop...")
        loop = agentic_loop
        loop.stop()
        logger.info("Stop signal sent")
    
    elif args.command == 'once':
        logger.info("Running one cycle of LivingAI Agentic Loop...")
        loop = agentic_loop
        loop.run_once()
        stats = loop.get_stats()
        logger.info(f"Cycle completed. Stats: {stats}")
    
    elif args.command == 'status':
        loop = agentic_loop
        tools = tools_integration
        
        print("\n" + "="*60)
        print("LivingAI V1+V2 - System Status")
        print("="*60)
        
        # Agentic loop status
        loop_stats = loop.get_stats()
        print(f"\nAgentic Loop:")
        print(f"  Status: {loop_stats['status']}")
        print(f"  Running: {loop_stats['running']}")
        print(f"  Current Task: {loop_stats['current_task'] or 'None'}")
        print(f"  Current Goal: {loop_stats['current_goal'] or 'None'}")
        print(f"  Cycles Completed: {loop_stats['cycles_completed']}")
        
        # Tools status
        tools_stats = tools.list_available_tools()
        print(f"\nTools:")
        print(f"  Available: {len(tools_stats)}")
        print(f"  First 10: {tools_stats[:10]}")
        
        # Agents status
        agent_manager = AgentManager()
        agents = agent_manager.list_agents()
        print(f"\nAgents:")
        print(f"  Total: {len(agents)}")
        for agent in agents:
            print(f"  - {agent}")
        
        print("\n" + "="*60)
    
    elif args.command == 'tools':
        if args.tools_command == 'list':
            tools = tools_integration
            available = tools.list_available_tools()
            print(f"\nAvailable Tools ({len(available)}):")
            print("-" * 40)
            for tool in available:
                info = tools.get_tool_info(tool)
                if info:
                    print(f"  {tool}: {info.get('description', 'No description')}")
                else:
                    print(f"  {tool}")
        
        elif args.tools_command == 'info':
            tools = tools_integration
            available = tools.list_available_tools()
            print(f"\nTool Information:")
            print("-" * 60)
            for tool in available:
                info = tools.get_tool_info(tool)
                if info:
                    print(f"\n{tool}:")
                    print(f"  Type: {info.get('tool_type', 'unknown')}")
                    print(f"  Description: {info.get('description', 'No description')}")
                    print(f"  Methods: {info.get('methods', [])}")
                    print(f"  Risk: {info.get('risk', 'unknown')}")
    
    elif args.command == 'agents':
        agent_manager = AgentManager()
        if args.agents_command == 'list':
            agents = agent_manager.list_agents()
            print(f"\nAgents ({len(agents)}):")
            print("-" * 40)
            for agent in agents:
                print(f"  - {agent}")
        
        elif args.agents_command == 'status':
            agents = agent_manager.list_agents()
            print(f"\nAgent Status:")
            print("-" * 60)
            for agent_id in agents:
                agent = agent_manager.get_agent(agent_id)
                if agent:
                    print(f"\n{agent_id}:")
                    print(f"  Status: {agent.status}")
                    print(f"  Current Task: {agent.current_task}")
                    print(f"  Tasks Completed: {agent.tasks_completed}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
