#version 430

struct Triangle {
    vec3 v0;
    float r;
    vec3 v1;
    float g;
    vec3 v2;
    float b;
    vec3 vn;
    float padding4;
};

struct Sphere {
    vec3 center;
    float radius;
    vec3 color;
    float roughness;
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

struct Triangle {
    vec3 v0;
    float r;
    vec3 v1;
    float g;
    vec3 v2;
    float b;
    vec3 vn;
    float padding4;
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
    vec3 color;
    float strength;
    float radius;
    vec3[6] points;
    int point_count;
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
layout(std430, binding = 5) buffer triangleData {
    Triangle[] triangles;
};

layout(std430, binding = 5) buffer triangleData {
    Triangle[] triangles;
};
layout(rgba32f, binding = 3) uniform image2DArray megaTexture;
layout(rgba32f, binding = 6) readonly uniform image2D noise;

uniform ivec4 objectCounts;
uniform int state;
uniform samplerCube skybox;

const float pi = 3.14159265f;

RenderState trace(Ray ray, float max_dist);

void hit(Ray ray, Sphere sphere, float tMin, float tMax, inout RenderState renderstate);

void hit(Ray ray, Plane plane, float tMin, float tMax, inout RenderState renderstate);

void hit(Ray ray, Light light, float tMin, float tMax, inout RenderState renderState);

void hit(Ray ray, Triangle triangle, float tMin, float tMax, inout RenderState renderstate);

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
    renderState.reflectivity = 1.0;
    //renderState.color = vec3(0.0);

    bool hasHit;
    for (int i = 0; i < 2; i++) {

        pixel = vec3(1.0);
        vec2 screenDeflection = imageLoad(
            noise, 
            ivec2(
                pixel_coords.x + i * screen_size.x,
                pixel_coords.y
            )
        ).xy;
        
        float horizontalCoefficient = float(pixel_coords.x);
        horizontalCoefficient = (horizontalCoefficient * 2 - screen_size.x) / screen_size.x;
        
        float verticalCoefficient = float(pixel_coords.y);
        verticalCoefficient = (verticalCoefficient * 2 - screen_size.y) / screen_size.x;

        
        ray.origin = viewer.position;
        ray.direction = viewer.forwards + horizontalCoefficient * viewer.right + verticalCoefficient * viewer.up;
        
    
        hasHit = false;

        for (int bounce = 0; bounce < bounce_count; bounce++) {
        

            renderState = trace(ray, 99999999);

            //early exit
            if (!renderState.hit && !hasHit) {
                pixel = vec3(texture(skybox,ray.direction));;
                break;
            }
            
            if(!renderState.hit){
                //If * instead of +, metal materials have softer colors that slightly resemble the skybox, idk which one is correct
                pixel = pixel + vec3(texture(skybox,ray.direction))/10;
                break;
            }


            hasHit = true;

            shadow_color = shadowCalc(renderState.position, renderState.normal);
        
            //unpack color
            pixel = (pixel * renderState.color) + light_fragment(renderState);
            pixel = pixel + (shadow_color) ;

            if(renderState.reflectivity <= 0.0){
                break;
            }

            //set up ray for next trace
            ray.origin = renderState.position;
            ray.direction = reflect(ray.direction, renderState.normal);
            vec3 variation = imageLoad(
                noise, 
                ivec2(
                    pixel_coords.x + bounce * screen_size.x,
                    pixel_coords.y
                )
            ).xyz;

            ray.direction = normalize(ray.direction + renderState.roughness);
        }

        finalColor += 0.5 * pixel;
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
    if ( state == 0) {
        for (int i = 0; i < objectCounts.w; i++) {
        
        hit(ray, triangles[i], 0.001, nearestHit, renderState);
        
        if (renderState.hit) {
                nearestHit = renderState.t;
                hitSomething = true;
            }
        }
    } else {
        for (int i = 0; i < objectCounts.x; i++) {

            hit(ray, spheres[i], 0.001, nearestHit, renderState);

            if (renderState.hit) {
                nearestHit = renderState.t;
                hitSomething = true;
            }
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

            vec3 d = renderState.position-sphere.center;
            d = d * sphere.radius;

            vec2 tex_coords = sphereUV_EqualArea(d);

            Material material = sample_material(2, tex_coords.x,tex_coords.y);

            renderState.position = ray.origin + t * ray.direction;
            renderState.normal = normalize(renderState.position - sphere.center);


            renderState.t = t;
            renderState.color = sphere.color;
            //renderState.roughness = material.roughness;
            //renderState.normal = material.normal;
            renderState.roughness = sphere.roughness;
            renderState.emissive = vec3(0.0);
            renderState.reflectivity = 0.5;
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
                renderState.emissive = material.emissive;
                renderState.roughness = material.roughness;
                renderState.reflectivity = material.gloss;
                // maps tangent space into world space
                mat3 TBN = mat3(plane.tangent, plane.bitangent, plane.normal);
                renderState.normal = normalize(TBN * material.normal);
                renderState.hit = true;
                return;
            }
        }
    }
    renderState.hit = false;
}

/*
Hit detection for triangle-type objects
*/
void hit(Ray ray, Triangle triangle, float tMin, float tMax, inout RenderState renderState) {

    renderState.hit = false;

    vec3 norm = triangle.vn;
    float ray_dot_tri = dot(ray.direction, norm);

    if (ray_dot_tri > 0.0) {
        norm = norm * -1;
        ray_dot_tri = ray_dot_tri * -1;
    }
    
    if (abs(ray_dot_tri) < 0.00001) {
        return;
    }

    mat3 system_matrix = mat3(ray.direction, triangle.v0 - triangle.v1, triangle.v0 - triangle.v2);
    float denominator = determinant(system_matrix);
    if (abs(denominator) < 0.00001) {
        return;
    }

    system_matrix = mat3(ray.direction, triangle.v0 - ray.origin, triangle.v0 - triangle.v2);
    float u = determinant(system_matrix) / denominator;
    if (u < 0.0 || u > 1.0) {
        return;
    }

    system_matrix = mat3(ray.direction, triangle.v0 - triangle.v1, triangle.v0 - ray.origin);
    float v = determinant(system_matrix) / denominator;
    if (v < 0.0 || u + v > 1.0) {
        return;
    }

    system_matrix = mat3(triangle.v0 - ray.origin, triangle.v0 - triangle.v1, triangle.v0 - triangle.v2);
    float t = determinant(system_matrix) / denominator;

    if (t > tMin && t < tMax) {

        renderState.position = ray.origin + t * ray.direction;
        renderState.normal = norm;
        renderState.t = t;
        renderState.color = vec3(triangle.r, triangle.g, triangle.b);
        renderState.hit = true;
    }
}


vec3 light_fragment(RenderState renderState){
    //ambient light
    vec3 color = vec3(0.0);

    for(int i = 0; i < objectCounts.z; i++)
    {
        bool blocked = false;

        Light light = lights[i];

        vec3 fragLight = light.position - renderState.position;

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
            //diffuse
            color += light.color * max(0.0, dot(renderState.normal, fragLight)) * light.strength / (distanceToLight * distanceToLight);
            //specular
            color += light.color * pow(max(0.0, dot(renderState.normal, halfway)),64) * light.strength / (distanceToLight * distanceToLight);
        }
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

    int counter;

    vec3 final_shadow = vec3(0.0);
    vec3 shadow_cont;

    for(int j = 0; j < objectCounts.z; j++){
        
        shadow_cont = vec3(0.0);
        counter = 0;

        for(int l = 0; l < lights[j].point_count; l++)
        {
            
            shadow_ray.direction = normalize(lights[j].points[l] - position);

            if(dot(shadow_ray.direction, normal) <= 0){
                continue;
            }

            light_dist = distance(lights[j].points[l],position);
            shadow_state = trace(shadow_ray,light_dist);
            if(!shadow_state.hit){
                shadow_cont += ((lights[j].color) * 1)/ (light_dist * light_dist);
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