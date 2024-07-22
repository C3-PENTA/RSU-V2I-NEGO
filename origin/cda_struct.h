//=============================================================================
// This confidential and proprietary software may be used only as authorized by
// a licensing agreement from CHEMTRONICS Limited.
//
// COPYRIGHT (c) CHEMTRONICS. ALL RIGHTS RESERVED.
//
// The entire notice above must be reproduced on all authorized copies and
// copies may only be made to the extent permitted by a licensing agreement
// from CHEMTRONICS Limited.
//
// Module: cda_struct.h
// Description: CDA Header of Socket Programming
//
// CDA : Cooperative Driving Automation
//
// Update History
// [07/31/2023 jongsik.kim] create
//=============================================================================
#ifndef _CDA_STRUCT_H_
#define _CDA_STRUCT_H_

/****************************************************************************************
 시스템 헤더
****************************************************************************************/
#include <stdint.h>

/****************************************************************************************
 상수 
****************************************************************************************/
#define DEF_SERVER_PORT                         63113
#define MAGIC_NUMBER                            0xf1f1
#define MAX_PIM_OBJECT                          255

/****************************************************************************************
 열거형
****************************************************************************************/
// Message Type (1byte)
typedef enum
{
	eCdaMsgHdrType_BSM_Noti		= 1,
	eCdaMsgHdrType_PIM_Noti		= 2,
	eCdaMsgHdrType_DMM_Noti		= 3,
	eCdaMsgHdrType_DNM_Req		= 4,
	eCdaMsgHdrType_DNM_Rep		= 5,
	eCdaMsgHdrType_DNM_Ack		= 6,
	eCdaMsgHdrType_EDM_Noti		= 7,
	eCdaMsgHdrType_MY_BSM_Noti	= 8,
	eCdaMsgHdrType_CIM_Noti		= 9,
	eCdaMsgHdrType_BSM_LIGHT_NOTI	= 51,
	eCdaMsgHdrType_L2ID_Req		= 101,
	eCdaMsgHdrType_L2ID_Resp	= 102,
	eCdaMsgHdrType_Light_Noti	= 103,
} eCdaMsgHdrType;

// Bit set (2bytes)
typedef enum
{
	eCdaExteriorLights_lowBeamHeadlightsOn		= 0,
	eCdaExteriorLights_highBeamHeadlightsOn		= 1,
	eCdaExteriorLights_leftTurnSignalOn			= 2,
	eCdaExteriorLights_rightTurnSignalOn		= 3,
	eCdaExteriorLights_hazardSignalOn			= 4,
	eCdaExteriorLights_automaticLightControlOn	= 5,
	eCdaExteriorLights_daytimeRunningLightsOn	= 6,
	eCdaExteriorLights_fogLightOn				= 7,
	eCdaExteriorLights_parkingLightsOn			= 8,
} eCdaExteriorLights;

/****************************************************************************************
 구조체
****************************************************************************************/
typedef struct
{
	short				magic;
	char				msg_type;
	short				crc16;
	short				len;
	char				data[0];
} __attribute__((__packed__)) CdaMsgHdr;

// BSM Data
typedef struct 
{
	uint8_t				msgCount; //1byte
	char				tmpID[4];     //4byte
	uint16_t			dSecond; //2byte
	int					latitude;
	int					longitude;
	short				elevation; //2byte
	//    uint32_t postionalAccuracy; //4byte
	uint8_t				semiMajor;
	uint8_t				semiMinor;
	uint16_t			orientation;
	uint16_t			transmissionAndSpeed;
	short				heading;
	uint8_t				steeringWheelAngle;
	//    uint8_t accelerationSet4Way[7]; //7byte
	short				accel_long;
	short				accel_lat;
	uint8_t				accel_vert;
	short				yawRate;
	uint16_t			brakeSystemStatus;
	//    uint8_t vehicleSize[3]; //3byte
	uint16_t			width;
	uint16_t			length;
	uint32_t			l2id;
} __attribute__((__packed__)) CdaBsmDataSt;  

typedef struct 
{
	CdaMsgHdr 			hdr;
	CdaBsmDataSt 		data;
} __attribute__((__packed__)) CdaBsmSt;

typedef struct 
{
	uint8_t				msgCount; //1byte
	char				tmpID[4];     //4byte
	uint16_t			dSecond; //2byte
	int					latitude;
	int					longitude;
	short				elevation; //2byte
	//    uint32_t postionalAccuracy; //4byte
	uint8_t				semiMajor;
	uint8_t				semiMinor;
	uint16_t			orientation;
	uint16_t			transmissionAndSpeed;
	short				heading;
	uint8_t				steeringWheelAngle;
	//    uint8_t accelerationSet4Way[7]; //7byte
	short				accel_long;
	short				accel_lat;
	uint8_t				accel_vert;
	short				yawRate;
	uint16_t			brakeSystemStatus;
	//    uint8_t vehicleSize[3]; //3byte
	uint16_t			width;
	uint16_t			length;
	uint32_t			l2id;
	uint16_t			light;
} 
__attribute__((__packed__)) CdaBsmAddLightDataSt;  

typedef struct 
{
	CdaMsgHdr 				hdr;
	CdaBsmAddLightDataSt 	data;
} __attribute__((__packed__)) CdaBsmAddLightSt;

// PIM Data
typedef struct
{
    uint8_t				objType;
    int					accuracy;
    uint16_t			objId;
    uint8_t				classification;
    int					outlierX1;
    int					outlierX2;
    int					outlierX3;
    int					outlierX4;
    int					outlierY1;
    int					outlierY2;
    int					outlierY3;
    int					outlierY4;
    int					velocityX;
    int					velocityY;
} __attribute__((__packed__)) CdaPimObjDataSt;

typedef struct
{
    char				mapOriginX[20];
    char				mapOriginY[20];
    int					crntLocX;
    int					crntLocY;
    int					crntLocHeading;
    int					dstLocX;
    int					dstLocY;
    uint16_t			objNum;
    CdaPimObjDataSt		pimObj[0];
} __attribute__((__packed__)) CdaPimDataSt;

typedef struct
{
    uint8_t				trafficLight;
    uint16_t			extLights;      // bit flag
} __attribute__((__packed__)) CdaPimExtDataSt;

typedef struct 
{
	CdaMsgHdr 			hdr;
	CdaPimObjDataSt 	data;
} __attribute__((__packed__)) CdaPimSt;

// DMM Data
typedef struct
{
    uint32_t			sender;
	uint32_t			receiver;
    uint16_t			maneuverType;
    uint8_t				remainDist;
} __attribute__((__packed__)) CdaDmmDataSt;

typedef struct 
{
	CdaMsgHdr 			hdr;
	CdaDmmDataSt 		data;
} __attribute__((__packed__)) CdaDmmSt;

// DNM Data
typedef struct
{
    uint32_t			sender;
    uint32_t			receiver;
    union 
    {
        uint8_t			remainDist;
        uint8_t			agreementFlag;
        uint8_t			negoDrivingDone;
    } __attribute__((__packed__)) dnmData;
} __attribute__((__packed__)) CdaDnmDataSt;

typedef struct 
{
	CdaMsgHdr 			hdr;
	CdaDnmDataSt 		data;
} __attribute__((__packed__)) CdaDnmSt;

// EDM Data
typedef struct
{
    uint32_t			sender;
    uint16_t			maneuverType;
    uint8_t				remainDist;
} __attribute__((__packed__)) CdaEdmDataSt;

typedef struct 
{
	CdaMsgHdr 			hdr;
	CdaEdmDataSt 		data;
} __attribute__((__packed__)) CdaEdmSt;

// CIM Data
typedef struct
{
    uint32_t			sender;
    uint8_t				vehicleType;
    char				vehicleColor[6];		// RGB Color
} __attribute__((__packed__)) CdaCimDataSt;

typedef struct 
{
	CdaMsgHdr 			hdr;
	CdaCimDataSt 		data;
} __attribute__((__packed__)) CdaCimSt;

// L2ID Data
typedef struct
{
	uint32_t			l2id;
} __attribute__((__packed__)) CdaL2IDRespDataSt;

typedef struct 
{
	CdaMsgHdr 			hdr;
} __attribute__((__packed__)) CdaL2IDReqSt;

typedef struct 
{
	CdaMsgHdr 			hdr;
	CdaL2IDRespDataSt	data;
} __attribute__((__packed__)) CdaL2IDRespSt;

// Light Notify
typedef struct
{
    uint16_t			light;
} __attribute__((__packed__)) CdaLightDataSt;

typedef struct 
{
	CdaMsgHdr 			hdr;
	CdaLightDataSt		data;
} __attribute__((__packed__)) CdaLightSt;

#endif	// _CDA_STRUCT_H_

