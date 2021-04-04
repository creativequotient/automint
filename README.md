# automint

Automated Cardano NFT minting framework

This project seeks to provide a suite of tools for NFT creators and content artists to automate the minting of their work.

## Features

### Batch IPFS uploader

An easy to use tool to batch upload and pin work via IPFS, capture and store IPFS addresses.

### Batch Minting Feature

Automated NFT minting tool using solely CSV or JSON files as inputs.

### Minting Validator

NFT minting validator tool. Given the current method of minting NFTs on Cardano (Prior of Goguen), NFTs are created as assets with `maximum supply` of 1. As a result, the minting process is succeptible to double minting, etc since there is no restriction on total supply of new tokens.

This tool will check that the tokens are minted according to specifications, no double minting, have proper metadata inserted, etc.
