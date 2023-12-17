#version 430

struct Sphere {
    vec3 center;
    float radius;
    vec3 color;
    float roughness;
    float reflectivity;
};

struct Camera {
    vec3 position;
    vec3 forwards;
    vec3 right;
    vec3 up;
};

struct Ray {
    vec3 origin;
    vec3 direction;
};

struct Plane {
    vec3 center;
    float uMin;
    vec3 tangent;
    float uMax;
    vec3 bitangent;
    float vMin;
    vec3 normal;
    float vMax;
    float material;
};

struct RenderState {
    float t;
    vec3 color;
    vec3 emissive;
    vec3 position;
    vec3 normal;
    bool hit;
    float roughness;
    float reflectivity;
};

struct Material {
    vec3 color;
    vec3 normal;
    vec3 emissive;
    vec3 specular;

    float roughness;
    float ao;
    float gloss;
    float displacement;
};

struct Light {
    vec3 position;
    float strength;
    vec3 color;
    float radius;
};

const float light_radius = 0.05;

const vec3[32] points = {
    vec3(light_radius, 0.0, 0.0),
    vec3(-light_radius, 0.0, 0.0),
    vec3(0.0, light_radius, 0.0),
    vec3(0.0, -light_radius, 0.0),
    vec3(0.0, 0.0, light_radius),
    vec3(0.0, 0.0, -light_radius),
    
    vec3(light_radius, light_radius, 0.0),
    vec3(light_radius, -light_radius, 0.0),
    vec3(-light_radius, light_radius, 0.0),
    vec3(-light_radius, -light_radius, 0.0),
    vec3(light_radius, 0.0, light_radius),
    vec3(light_radius, 0.0, -light_radius),
    vec3(-light_radius, 0.0, light_radius),
    vec3(-light_radius, 0.0, -light_radius),
    vec3(0.0, light_radius, light_radius),
    vec3(0.0, light_radius, -light_radius),
    vec3(0.0, -light_radius, light_radius),
    vec3(0.0, -light_radius, -light_radius),
    
    vec3(light_radius, light_radius, light_radius),
    vec3(light_radius, light_radius, -light_radius),
    vec3(light_radius, -light_radius, light_radius),
    vec3(light_radius, -light_radius, -light_radius),
    vec3(-light_radius, light_radius, light_radius),
    vec3(-light_radius, light_radius, -light_radius),
    vec3(-light_radius, -light_radius, light_radius),
    vec3(-light_radius, -light_radius, -light_radius),

    vec3(0.0, light_radius, light_radius),
    vec3(0.0, light_radius, -light_radius),
    vec3(0.0, -light_radius, light_radius),
    vec3(0.0, -light_radius, -light_radius),

    vec3(light_radius, 0.0, light_radius),
    vec3(light_radius, 0.0, -light_radius)
};



// input/output
layout(local_size_x = 8, local_size_y = 8) in;
layout(rgba32f, binding = 0) uniform image2D img_output;

//Scene data
uniform Camera viewer;
layout(std430, binding = 1) buffer sphereData {
    Sphere[] spheres;
};
layout(std430, binding = 2) buffer planeData {
    Plane[] planes;
};
layout(std430, binding = 4) buffer lightData{
    Light[] lights;
};

layout(rgba32f, binding = 3) uniform image2DArray megaTexture;
layout(rgba32f, binding = 6) readonly uniform image2D noise;

uniform ivec3 objectCounts;
uniform samplerCube skybox;

const float pi = 3.14159265f;

RenderState trace(Ray ray, float max_dist);

void hit(Ray ray, Sphere sphere, float tMin, float tMax, inout RenderState renderstate);

void hit(Ray ray, Plane plane, float tMin, float tMax, inout RenderState renderstate);

void hit(Ray ray, Light light, float tMin, float tMax, inout RenderState renderState);

Material sample_material(float index, float u, float v);

float distanceTo(Ray ray, Sphere sphere);
float distanceTo(Ray ray, Plane plane);

vec3 shadowCalc(vec3 position, vec3 normal);

vec3 light_fragment(RenderState renderState);

vec2 sphereUV_equirectangular(vec3 d);

vec2 sphereUV_EqualArea(vec3 d);

void main() {

    ivec2 pixel_coords = ivec2(gl_GlobalInvocationID.xy);
    ivec2 screen_size = imageSize(img_output);

    int bounce_count = 16;
    int counter = 4;

    vec3 finalColor = vec3(0.0);
    vec3 shadow_color = vec3(0.0);
    vec3 pixel;
    Ray ray;
    RenderState renderState;
    renderState.reflectivity = 0.0;
    renderState.hit = false;
    //renderState.color = vec3(0.0);


    bool hasHit;
    for (int i = 0; i < 1; i++) {

        pixel = vec3(1.0);
        /*vec2 screenDeflection = imageLoad(
            noise, 
            ivec2(
                pixel_coords.x + i * screen_size.x,
                pixel_coords.y
            )
        ).xy;*/
        
        float horizontalCoefficient = float(pixel_coords.x);
        horizontalCoefficient = (horizontalCoefficient * 2 - screen_size.x) / screen_size.x;
        
        float verticalCoefficient = float(pixel_coords.y);
        verticalCoefficient = (verticalCoefficient * 2 - screen_size.y) / screen_size.x;

        
        ray.origin = viewer.position;
        ray.direction = viewer.forwards + horizontalCoefficient * viewer.right + verticalCoefficient * viewer.up;
        
    
        hasHit = false;

        for (int bounce = 0; bounce < bounce_count; bounce++) {
        

            renderState = trace(ray, 99999999);

            if(!hasHit){
                if(!renderState.hit){
                    pixel = vec3(texture(skybox,ray.direction));
                    break;
                }else{
                    hasHit = true;
                }
            }
            else{
                if(!renderState.hit){
                    pixel = pixel + vec3(texture(skybox,ray.direction));
                    break;
                }
            }
       
        
            pixel = (pixel * renderState.color) + light_fragment(renderState);

            

            if(renderState.reflectivity <= 0.0){
                break;
            }

            //set up ray for next trace
            ray.origin = renderState.position;
            ray.direction = reflect(ray.direction, renderState.normal);
            /*vec3 variation = imageLoad(
                noise, 
                ivec2(
                    pixel_coords.x + bounce * screen_size.x,
                    pixel_coords.y
                )
            ).xyz;*/

            ray.direction = normalize(ray.direction + renderState.roughness);
        }

        finalColor += 1 * pixel;
    }

    imageStore(img_output, pixel_coords, vec4(finalColor,1.0));
}

/*
Does the ray tracing calculations
*/
RenderState trace(Ray ray,float max_dist) {

    RenderState renderState;
    renderState.hit = false;
    renderState.color = vec3(0.0);
    bool hitSomething = false;
    
    float nearestHit = max_dist;
    
    for (int i = 0; i < objectCounts.x; i++) {

        hit(ray, spheres[i], 0.001, nearestHit, renderState);

        if (renderState.hit) {
            nearestHit = renderState.t;
            hitSomething = true;
        }
    }

    for (int i = 0; i < objectCounts.y; i++) {
    
       hit(ray, planes[i], 0.001, nearestHit, renderState);
    
       if (renderState.hit) {
            nearestHit = renderState.t;
            hitSomething = true;
        }
    }

    if (hitSomething) {
        renderState.hit = true;
    }

        
    return renderState;
}

/*
Hit detection for sphere-type objects
*/
void hit(Ray ray, Sphere sphere, float tMin, float tMax, inout RenderState renderState) {

    vec3 co = ray.origin - sphere.center;
    float a = dot(ray.direction, ray.direction);
    float b = 2 * dot(ray.direction, co);
    float c = dot(co, co) - sphere.radius * sphere.radius;
    float discriminant = b * b - (4 * a * c);
    
    if (discriminant > 0.0) {

        float t = (-b - sqrt(discriminant)) / (2 * a);

        if (t > tMin && t < tMax) {

            /*vec3 d = renderState.position-sphere.center;
            d = normalize(d);

            vec2 tex_coords = sphereUV_equirectangular(d);

            Material material = sample_material(2, tex_coords.x,tex_coords.y);*/

            renderState.position = ray.origin + t * ray.direction;
            renderState.normal = normalize(renderState.position - sphere.center);


            renderState.t = t;
            //renderState.color = vec3(0.0);
            renderState.color = sphere.color;
            //renderState.color = material.color;
            renderState.roughness = sphere.roughness;
            //renderState.roughness = material.roughness;
            //renderState.normal = material.normal;
            renderState.emissive = vec3(0.0);
            renderState.reflectivity = sphere.reflectivity;
            renderState.hit = true;
            return;
        }
    }
    renderState.hit = false;
}

/*
Hit detection for plane-type objects
*/
void hit(Ray ray, Plane plane, float tMin, float tMax, inout RenderState renderState) {
    
    float denom = dot(plane.normal, ray.direction); 
    
    if (abs(denom) > 0.000001) {

        float t = dot(plane.center - ray.origin, plane.normal) / denom; 

        if (t > tMin && t < tMax) {

            vec3 testPoint = ray.origin + t * ray.direction;
            vec3 testDirection = testPoint - plane.center;

            float u = dot(testDirection, plane.tangent);
            float v = dot(testDirection, plane.bitangent);

            if (u > plane.uMin && u < plane.uMax && v > plane.vMin && v < plane.vMax) {

                u = (u - plane.uMin) / (plane.uMax - plane.uMin);
                v = (v - plane.vMin) / (plane.vMax - plane.vMin);

                Material material = sample_material(plane.material, u, v);

                renderState.position = testPoint;
                renderState.t = t;
                renderState.color = material.color;
                //renderState.color = vec3(0.5,0.4,0.8);
                renderState.emissive = material.emissive;
                renderState.roughness = material.roughness;
                renderState.reflectivity = material.gloss;
                // maps tangent space into world space
                mat3 TBN = mat3(plane.tangent, plane.bitangent, plane.normal);
                renderState.normal = normalize(TBN * material.normal);
                renderState.normal = plane.normal;
                renderState.hit = true;
                return;
            }
        }
    }
    renderState.hit = false;
}

void hit(Ray ray, Light light, float tMin, float tMax, inout RenderState renderState){
    
    vec3 co = ray.origin - light.position;
    float a = dot(ray.direction, ray.direction);
    float b = 2* dot(ray.direction,co);
    float c = dot(co,co) - 0.25 * 0.25;
    float discriminant = b * b - (4*a*c);

    if(discriminant > 0.0){
        float t = (-b - sqrt(discriminant)) / (2 * a);

        if (t > tMin && t < tMax) {

            float dist = length(ray.origin-light.position);
            renderState.t = t;
            renderState.color = light.color*light.strength;
            renderState.roughness = 0;
            renderState.normal = vec3(0.0);
            renderState.emissive = vec3(0.0);
            renderState.reflectivity = 0.0;
            renderState.hit = true;
            return;
        }
    }
    renderState.hit = false;
}

vec3 light_fragment(RenderState renderState){
    //ambient light
    vec3 color = vec3(0.0);

    int counter;

    for(int i = 0; i < objectCounts.z; i++)
    {
        
        counter = 0;
        Light light = lights[i];

        for(int l = 0; l < 32; l++){

        
            bool blocked = false;
            vec3 fragLight = (light.position + points[l]) - renderState.position;

            if(dot(fragLight, renderState.normal) <= 0){
                continue;
            }

            float distanceToLight = length(fragLight);
            fragLight = normalize(fragLight);

            vec3 fragViewer = normalize(viewer.position - renderState.position);

            vec3 halfway = normalize(fragViewer + fragLight);

            Ray ray;
            ray.origin = renderState.position;
            ray.direction = fragLight;

            for(int j = 0; j < objectCounts.x; j++){

                float trialDist = distanceTo(ray, spheres[j]);

                if (trialDist < distanceToLight) {
                    blocked = true;
                    break;
                }
            }
            if (blocked) {
                continue;
            }

            for (int j = 0; j < objectCounts.y; j++) {
            
                float trialDist = distanceTo(ray, planes[j]);

                if (trialDist < distanceToLight) {
                    blocked = true;
                    break;
                }
            }


            if (!blocked) {
                //Apply lighting
                //diffuse 0.03125
                counter++;
                color += 0.03125 * light.color * max(0.0, dot(renderState.normal, fragLight)) * light.strength / (distanceToLight*distanceToLight);
                //specular
                color += 0.03125 * light.color * pow(max(0.0, dot(renderState.normal, halfway)),64) * light.strength / (distanceToLight*distanceToLight);
            }
        }

        // if(counter > 0){
        //     color = color / counter;
        // }
        

    }

    return color;
}

/*
Distance from ray origin to a sphere
*/
float distanceTo(Ray ray, Sphere sphere){

    vec3 co = ray.origin - sphere.center;
    float a = dot(ray.direction, ray.direction);
    float b = 2 * dot(ray.direction, co);
    float c = dot(co, co) - sphere.radius * sphere.radius;
    float discriminant = b * b - (4 * a * c);
    
    if (discriminant > 0.0) {

        float t = (-b - sqrt(discriminant)) / (2 * a);

        if (t < 0.0001) {
            return 9999;
        }

        return length(t * ray.direction);
    }

    return 99999;
}

/*
Distance from ray origin to a plane
*/
float distanceTo(Ray ray, Plane plane){

    float denom = dot(plane.normal, ray.direction); 
    
    if (denom < 0.000001) {

        float t = dot(plane.center - ray.origin, plane.normal) / denom; 

        if (t < 0.0001) {
            return 9999;
        }

        vec3 testPoint = ray.origin + t * ray.direction;
        vec3 testDirection = testPoint - plane.center;

        float u = dot(testDirection, plane.tangent);
        float v = dot(testDirection, plane.bitangent);

        if (u > plane.uMin && u < plane.uMax && v > plane.vMin && v < plane.vMax) {
            return length(t * ray.direction);
        }
    }
    return 9999;
}


/*
Returns all map values for a given texture contained in the megatexture based on the provided index and (u,v) coordinates
*/
Material sample_material(float index, float u, float v) {

    Material material;
    ivec3 baseCoords = ivec3(floor(1024 * u), floor(1024 * v), index);
    ivec3 nextImage  = ivec3(1024, 0, 0);

    /*
    material.color          = texture(megaTexture, baseCoords).rgb;
    material.displacement   = texture(megaTexture, baseCoords + 1 * nextImage).r;
    material.normal         = texture(megaTexture, baseCoords + 2 * nextImage).rgb;
    material.normal         = 2.0 * material.normal - vec3(1.0);
    material.roughness      = texture(megaTexture, baseCoords + 3 * nextImage).r;
    material.gloss          = texture(megaTexture, baseCoords + 4 * nextImage).r;
    material.specular       = texture(megaTexture, baseCoords + 5 * nextImage).rgb;
    material.emissive       = texture(megaTexture, baseCoords + 6 * nextImage).rgb;
    material.ao             = texture(megaTexture, baseCoords + 7 * nextImage).r;
    */
    
    material.color          = imageLoad(megaTexture, baseCoords).rgb;
    material.displacement   = imageLoad(megaTexture, baseCoords + 1 * nextImage).r;
    material.normal         = imageLoad(megaTexture, baseCoords + 2 * nextImage).rgb;
    material.normal         = 2.0 * material.normal - vec3(1.0);
    material.roughness      = imageLoad(megaTexture, baseCoords + 3 * nextImage).r;
    material.gloss          = imageLoad(megaTexture,baseCoords + 4 * nextImage).r;
    material.specular       = imageLoad(megaTexture, baseCoords + 5 * nextImage).rgb;
    material.emissive          = imageLoad(megaTexture, baseCoords + 6 * nextImage).rgb;
    material.ao                = imageLoad(megaTexture, baseCoords + 7 * nextImage).r;

    return material;
}

vec3 shadowCalc(vec3 position, vec3 normal){

    Ray shadow_ray;

    shadow_ray.origin = position;
    RenderState shadow_state;

    float light_dist;
    vec3 light_point;

    int counter;

    vec3 final_shadow = vec3(0.0);
    vec3 shadow_cont;

    vec3 rand = vec3(0.0);

    for(int j = 0; j < objectCounts.z; j++){
        
        shadow_cont = vec3(0.0);
        counter = 0;

        for(int l = 0; l < 16; l++)
        {
            
            rand = imageLoad(noise, ivec2(j+1,l+1)).xyz;
            light_point = points[l]*lights[j].radius+ lights[j].position + rand;
            shadow_ray.direction = normalize(light_point - position);

            if(dot(shadow_ray.direction, normal) <= 0){
                continue;
            }

            light_dist = distance(light_point,position);
            shadow_state = trace(shadow_ray,light_dist);
            if(!shadow_state.hit){
                shadow_cont += ((lights[j].color) * lights[j].strength * max(0.0,dot(normal, shadow_ray.direction)))/ (light_dist * light_dist);
                counter++;
            }
        }
        if(counter > 0)
        {
            shadow_cont = shadow_cont/counter;
        }
        final_shadow += shadow_cont;
    }
    return final_shadow;
}


vec2 sphereUV_equirectangular(vec3 d){

    vec2 uv = vec2(0.0);

    uv.x = 0.5 + atan(d.y,d.x)/(2*pi);
    uv.y = 0.5 + asin(d.z);

    return uv;
}

vec2 sphereUV_EqualArea(vec3 d){

    vec2 uv = vec2(0.0);

    uv.x = 0.5 * (atan(d.y,-d.x)/(pi+1));
    uv.y = 0.5 + (asin(d.z)/pi);

    return uv;
}